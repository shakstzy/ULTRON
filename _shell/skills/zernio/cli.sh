#!/bin/bash
# zernio cli.sh - direct REST wrapper for the Zernio API (zernio.com/api/v1).
# Single-entry CLI for organic publishing AND paid ads (same API key).
#
# Reads (no gate):
#   accounts                                       list connected social accounts
#   creator-info <accountId> [video|photo]         TikTok creator-info precheck
#   discord-channels <accountId>                   Discord: list channels (falls back to accounts metadata if live API not ready)
#   discord-settings <accountId>                   Discord: current channel + webhook identity
#   status <postId>                                poll a post to terminal state
#   ad-accounts [accountId]                        list platform ad accounts
#   list-ads [adAccountId] [platform]              list ads, optionally scoped
#   get-ad <adId>                                  one ad incl. metrics
#   ad-analytics <adId> [from] [to]                daily ad analytics
#   ad-comments <adId>                             comments on an ad's underlying post
#   tree [adAccountId]                             Campaign > AdSet > Ad with metrics
#   list-campaigns [adAccountId]                   list campaigns
#   list-audiences [adAccountId]                   list custom audiences
#   get-audience <audienceId>                      one audience
#   search-interests <q> <accountId> [platform]    interest IDs lookup
#   conversion-destinations <accountId>            list pixels / conversion actions
#
# Local file ops (no network, no gate):
#   preflight <file> <platform> [surface]          offline media validation
#   presign <file>                                 get upload URL
#   upload <file>                                  presign + PUT, returns publicUrl
#
# Writes (PUBLISH gate enforced by caller):
#   post <payload.json>                            organic publish
#   discord-settings-update <accountId> <payload.json>  PATCH webhook identity / switch channel
#
# Writes (LAUNCH-AD gate enforced by caller):
#   boost-post <payload.json>
#   create-ad <payload.json>
#   create-ctwa <payload.json>
#   update-ad <adId> <payload.json>
#   cancel-ad <adId>
#   update-campaign <campaignId> <payload.json>
#   campaign-status <campaignId> <ACTIVE|PAUSED>
#   delete-campaign <campaignId>
#   duplicate-campaign <campaignId> [payload.json]
#   bulk-status <payload.json>
#   update-ad-set <adSetId> <payload.json>
#   ad-set-status <adSetId> <ACTIVE|PAUSED>
#   create-audience <payload.json>
#   add-audience-users <audienceId> <payload.json>
#   delete-audience <audienceId>
#   send-conversions <payload.json>
#   connect-ads <facebook|instagram|linkedin|pinterest|tiktok|twitter|googleads> [accountId]
#
# Requires: ZERNIO_API_KEY in env, curl, jq, file. ffprobe optional (for video preflight).

set -euo pipefail

BASE_URL="https://zernio.com/api/v1"

die() { echo "zernio: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

[[ -n "${ZERNIO_API_KEY:-}" ]] || die "ZERNIO_API_KEY not set (lives in .claude/settings.local.json)"
have curl || die "curl not found"
have jq   || die "jq not found"
have file || die "file (libmagic) not found"

filesize() {
  if stat -f%z "$1" >/dev/null 2>&1; then stat -f%z "$1"; else stat -c%s "$1"; fi
}

# api METHOD PATH [BODY] - surfaces real HTTP errors, special-cases the Ads add-on paywall.
api() {
  local method="$1" path="$2" body="${3:-}"
  local tmp http resp
  tmp=$(mktemp)
  if [[ -n "$body" ]]; then
    http=$(curl -sS -o "$tmp" -w "%{http_code}" -X "$method" \
      -H "Authorization: Bearer ${ZERNIO_API_KEY}" \
      -H "Content-Type: application/json" \
      --data "$body" \
      "${BASE_URL}${path}")
  else
    http=$(curl -sS -o "$tmp" -w "%{http_code}" -X "$method" \
      -H "Authorization: Bearer ${ZERNIO_API_KEY}" \
      "${BASE_URL}${path}")
  fi
  resp=$(cat "$tmp"); rm -f "$tmp"
  if [[ "$http" -ge 200 && "$http" -lt 300 ]]; then
    printf '%s' "$resp"
    return 0
  fi
  if echo "$resp" | grep -qi "Ads add-on required"; then
    die "HTTP ${http} from ${path}: Ads add-on not enabled. Enable at zernio.com/settings/billing (Build \$10/mo, Accelerate \$50/unit, Unlimited \$1k/mo)."
  fi
  die "HTTP ${http} from ${path}: ${resp}"
}

# URL-encode a string. Pure bash so no python/jq dependency for query helpers.
urlenc() {
  local s="$1" i c out=""
  for ((i=0; i<${#s}; i++)); do
    c="${s:i:1}"
    case "$c" in
      [a-zA-Z0-9.~_-]) out+="$c" ;;
      *) printf -v c '%%%02X' "'$c"; out+="$c" ;;
    esac
  done
  printf '%s' "$out"
}

# Build a query string from key=value pairs. Values are URL-encoded; empty values skipped.
qs() {
  local out=""
  for kv in "$@"; do
    local k="${kv%%=*}" v="${kv#*=}"
    [[ -z "$v" ]] && continue
    local ev; ev=$(urlenc "$v")
    if [[ -z "$out" ]]; then out="?${k}=${ev}"; else out="${out}&${k}=${ev}"; fi
  done
  printf '%s' "$out"
}

ads_platform_ok() {
  case "$1" in
    metaads|googleads|linkedinads|tiktokads|pinterestads|xads) return 0 ;;
    *) return 1 ;;
  esac
}

connect_platform_ok() {
  case "$1" in
    facebook|instagram|linkedin|pinterest|tiktok|twitter|googleads) return 0 ;;
    *) return 1 ;;
  esac
}

cmd="${1:-}"; shift || true

case "$cmd" in
  # ---------- reads ----------
  accounts)
    api GET /accounts
    ;;

  creator-info)
    accountId="${1:?accountId required}"
    mediaType="${2:-video}"
    api GET "/accounts/${accountId}/tiktok/creator-info?mediaType=${mediaType}"
    ;;

  discord-channels)
    accountId="${1:?accountId required}"
    # Live API doesn't ship /accounts/{id}/discord-channels yet (returns 404 HTML
    # as of 2026-04-29). The connected channel lives in accounts[].metadata, so
    # degrade to that. Switch back to direct call when Zernio ships the endpoint.
    resp=$(api GET "/accounts/${accountId}/discord-channels" 2>/dev/null) || resp=""
    if [[ -n "$resp" ]] && echo "$resp" | jq empty 2>/dev/null; then
      printf '%s' "$resp"
    else
      "$0" accounts | jq --arg id "$accountId" '
        .accounts[]
        | select(._id == $id and .platform == "discord")
        | {
            connectedChannel: { id: .metadata.channelId, name: .metadata.channelName, type: .metadata.channelType },
            guild: { id: .metadata.guildId, name: .metadata.guildName },
            note: "discord-channels endpoint not live; reading from accounts metadata"
          }
      '
    fi
    ;;

  discord-settings)
    accountId="${1:?accountId required}"
    resp=$(api GET "/accounts/${accountId}/discord-settings" 2>/dev/null) || resp=""
    if [[ -n "$resp" ]] && echo "$resp" | jq empty 2>/dev/null; then
      printf '%s' "$resp"
    else
      "$0" accounts | jq --arg id "$accountId" '
        .accounts[]
        | select(._id == $id and .platform == "discord")
        | {
            channel: { id: .metadata.channelId, name: .metadata.channelName, type: .metadata.channelType },
            guild: { id: .metadata.guildId, name: .metadata.guildName },
            webhook: { id: .metadata.webhookId, hasToken: (.metadata.webhookToken != null) },
            connectionMethod: .metadata.connectionMethod,
            note: "discord-settings endpoint not live; reading from accounts metadata"
          }
      '
    fi
    ;;

  status)
    postId="${1:?postId required}"
    api GET "/posts/${postId}"
    ;;

  ad-accounts)
    accountId="${1:-}"
    api GET "/ads/accounts$(qs accountId="$accountId")"
    ;;

  list-ads)
    adAccountId="${1:-}"; platform="${2:-}"
    if [[ -n "$platform" ]] && ! ads_platform_ok "$platform"; then
      die "list-ads: bad platform '$platform' (use metaads|googleads|linkedinads|tiktokads|pinterestads|xads)"
    fi
    api GET "/ads$(qs adAccountId="$adAccountId" platform="$platform")"
    ;;

  get-ad)
    adId="${1:?adId required}"
    api GET "/ads/${adId}"
    ;;

  ad-analytics)
    adId="${1:?adId required}"; fromDate="${2:-}"; toDate="${3:-}"
    api GET "/ads/${adId}/analytics$(qs fromDate="$fromDate" toDate="$toDate")"
    ;;

  ad-comments)
    adId="${1:?adId required}"
    api GET "/ads/${adId}/comments"
    ;;

  tree)
    adAccountId="${1:-}"
    api GET "/ads/tree$(qs adAccountId="$adAccountId")"
    ;;

  list-campaigns)
    adAccountId="${1:-}"
    api GET "/ads/campaigns$(qs adAccountId="$adAccountId")"
    ;;

  list-audiences)
    adAccountId="${1:-}"
    api GET "/ads/audiences$(qs adAccountId="$adAccountId")"
    ;;

  get-audience)
    audienceId="${1:?audienceId required}"
    api GET "/ads/audiences/${audienceId}"
    ;;

  search-interests)
    q="${1:?query required}"; accountId="${2:?accountId required}"; platform="${3:-}"
    if [[ -n "$platform" ]] && ! ads_platform_ok "$platform"; then
      die "search-interests: bad platform '$platform'"
    fi
    api GET "/ads/interests$(qs q="$q" accountId="$accountId" platform="$platform")"
    ;;

  conversion-destinations)
    accountId="${1:?accountId required}"
    api GET "/accounts/${accountId}/conversion-destinations"
    ;;

  # ---------- local file ops ----------
  preflight)
    file="${1:?file required}"
    platform="${2:?platform required (instagram|youtube|tiktok|discord)}"
    surface="${3:-}"
    [[ -f "$file" ]] || die "file not found: $file"
    [[ -s "$file" ]] || die "file is empty: $file"
    size=$(filesize "$file")
    mime=$(file -b --mime-type "$file")
    case "$platform" in
      instagram)
        case "$mime" in
          image/jpeg|image/png) max=$((8*1024*1024)) ;;
          video/mp4|video/quicktime)
            case "$surface" in
              story)                  max=$((100*1024*1024)) ;;
              reels|feed|carousel|"") max=$((300*1024*1024)) ;;
              *) die "instagram: unknown surface '$surface' (use feed|story|reels|carousel)" ;;
            esac
            ;;
          *) die "instagram: unsupported mime: $mime (expected image/jpeg, image/png, video/mp4, video/quicktime)" ;;
        esac
        [[ "$size" -le "$max" ]] || die "instagram: file size $size exceeds cap $max for surface=${surface:-feed}"
        ;;
      youtube)
        case "$mime" in
          video/mp4|video/quicktime|video/x-msvideo|video/x-ms-wmv|video/x-flv|video/3gpp|video/webm) ;;
          *) die "youtube: unsupported mime: $mime" ;;
        esac
        ;;
      tiktok)
        case "$mime" in
          video/mp4|video/quicktime|video/webm)
            max=$((4*1024*1024*1024))
            [[ "$size" -le "$max" ]] || die "tiktok: video size $size exceeds 4GB cap"
            ;;
          image/jpeg|image/png|image/webp)
            max=$((20*1024*1024))
            [[ "$size" -le "$max" ]] || die "tiktok: image size $size exceeds 20MB cap"
            ;;
          *) die "tiktok: unsupported mime: $mime" ;;
        esac
        ;;
      twitter)
        case "$mime" in
          image/jpeg|image/png|image/webp)
            max=$((5*1024*1024))
            [[ "$size" -le "$max" ]] || die "twitter: image size $size exceeds 5MB cap"
            ;;
          image/gif)
            max=$((15*1024*1024))
            [[ "$size" -le "$max" ]] || die "twitter: GIF size $size exceeds 15MB cap"
            ;;
          video/mp4|video/quicktime)
            max=$((512*1024*1024))
            [[ "$size" -le "$max" ]] || die "twitter: video size $size exceeds 512MB cap"
            ;;
          *) die "twitter: unsupported mime: $mime" ;;
        esac
        ;;
      discord)
        # Default 25MB. Boosted servers go up to 500MB; pass surface=boosted to opt in.
        case "$mime" in
          image/jpeg|image/png|image/gif|image/webp)
            max=$((25*1024*1024))
            [[ "$size" -le "$max" ]] || die "discord: image size $size exceeds 25MB cap"
            ;;
          video/mp4|video/quicktime|video/webm)
            case "$surface" in
              boosted)     max=$((500*1024*1024)) ;;
              ""|standard) max=$((25*1024*1024)) ;;
              *) die "discord: unknown surface '$surface' (use standard|boosted)" ;;
            esac
            [[ "$size" -le "$max" ]] || die "discord: video size $size exceeds ${max} cap (surface=${surface:-standard}; pass 'boosted' for boosted-server cap)"
            ;;
          *) die "discord: unsupported mime: $mime (expected image/jpeg|png|gif|webp or video/mp4|quicktime|webm)" ;;
        esac
        ;;
      *) die "unknown platform: $platform" ;;
    esac
    result=$(jq -n \
      --arg file "$file" --argjson size "$size" --arg mime "$mime" --arg platform "$platform" --arg surface "$surface" \
      '{file:$file, size:$size, mime:$mime, platform:$platform, surface:$surface, warnings:[]}')
    if have ffprobe && [[ "$mime" == video/* ]]; then
      duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$file" 2>/dev/null || echo "")
      dims=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$file" 2>/dev/null || echo "")
      result=$(echo "$result" | jq --arg d "$duration" --arg dims "$dims" '. + {duration_s:$d, dims:$dims}')
      width="${dims%%x*}"; height="${dims##*x}"
      if [[ "$platform" == "instagram" && "$surface" == "reels" ]]; then
        awk "BEGIN{exit !($duration > 90)}" && die "instagram reels: duration ${duration}s exceeds 90s cap"
      fi
      if [[ "$platform" == "instagram" && "$surface" == "story" ]]; then
        awk "BEGIN{exit !($duration > 60)}" && die "instagram story: duration ${duration}s exceeds 60s cap"
      fi
      if [[ "$platform" == "tiktok" ]]; then
        awk "BEGIN{exit !($duration < 3)}"   && die "tiktok: duration ${duration}s under 3s minimum"
        awk "BEGIN{exit !($duration > 600)}" && die "tiktok: duration ${duration}s over 10min cap"
        [[ -n "$width" && -n "$height" && "$height" -gt "$width" ]] || die "tiktok: aspect must be 9:16 vertical (got ${dims})"
      fi
      if [[ "$platform" == "twitter" ]]; then
        awk "BEGIN{exit !($duration > 140)}" && die "twitter: video duration ${duration}s exceeds 140s cap (use longVideo for Premium)"
      fi
    fi
    echo "$result"
    ;;

  presign)
    file="${1:?file required}"
    [[ -f "$file" ]] || die "file not found: $file"
    fileName=$(basename "$file")
    mime=$(file -b --mime-type "$file")
    # Live API uses lowercase `filename` and `contentType`, despite docs showing fileName/fileType. Verified 2026-04-20.
    body=$(jq -n --arg fn "$fileName" --arg ct "$mime" '{filename:$fn, contentType:$ct}')
    api POST /media/presign "$body"
    ;;

  upload)
    file="${1:?file required}"
    [[ -f "$file" ]] || die "file not found: $file"
    mime=$(file -b --mime-type "$file")
    # Zernio presign returns `expiresIn` in seconds (TTL), not absolute timestamp. Verified 2026-04-20.
    for attempt in 1 2; do
      resp=$("$0" presign "$file")
      uploadUrl=$(echo "$resp" | jq -r .uploadUrl)
      publicUrl=$(echo "$resp" | jq -r .publicUrl)
      expiresIn=$(echo "$resp" | jq -r .expiresIn)
      [[ "$uploadUrl" != "null" && -n "$uploadUrl" ]] || die "presign returned no uploadUrl: $resp"
      if [[ "$expiresIn" != "null" && -n "$expiresIn" && "$expiresIn" -lt 60 ]]; then
        [[ $attempt -lt 2 ]] && continue || die "upload: presigned URL TTL ${expiresIn}s under 60s after refresh"
      fi
      curl -sS -f -X PUT -H "Content-Type: $mime" --data-binary "@${file}" "$uploadUrl" >/dev/null
      jq -n --arg u "$publicUrl" --argjson e "${expiresIn:-0}" '{publicUrl:$u, expiresIn:$e}'
      exit 0
    done
    ;;

  # ---------- writes (PUBLISH gate) ----------
  post)
    payload="${1:?payload.json required}"
    [[ -f "$payload" ]] || die "payload file not found: $payload"
    api POST /posts "$(cat "$payload")"
    ;;

  discord-settings-update)
    accountId="${1:?accountId required}"
    payload="${2:?payload.json required}"
    [[ -f "$payload" ]] || die "payload file not found: $payload"
    api PATCH "/accounts/${accountId}/discord-settings" "$(cat "$payload")"
    ;;

  # ---------- writes (LAUNCH-AD gate) ----------
  boost-post)
    payload="${1:?payload.json required}"; [[ -f "$payload" ]] || die "payload not found: $payload"
    api POST /ads/boost "$(cat "$payload")"
    ;;

  create-ad)
    payload="${1:?payload.json required}"; [[ -f "$payload" ]] || die "payload not found: $payload"
    api POST /ads/create "$(cat "$payload")"
    ;;

  create-ctwa)
    payload="${1:?payload.json required}"; [[ -f "$payload" ]] || die "payload not found: $payload"
    api POST /ads/ctwa "$(cat "$payload")"
    ;;

  update-ad)
    adId="${1:?adId required}"; payload="${2:?payload.json required}"
    [[ -f "$payload" ]] || die "payload not found: $payload"
    api PUT "/ads/${adId}" "$(cat "$payload")"
    ;;

  cancel-ad)
    adId="${1:?adId required}"
    api DELETE "/ads/${adId}"
    ;;

  update-campaign)
    campaignId="${1:?campaignId required}"; payload="${2:?payload.json required}"
    [[ -f "$payload" ]] || die "payload not found: $payload"
    api PUT "/ads/campaigns/${campaignId}" "$(cat "$payload")"
    ;;

  campaign-status)
    campaignId="${1:?campaignId required}"; status="${2:?status required (ACTIVE|PAUSED)}"
    [[ "$status" == "ACTIVE" || "$status" == "PAUSED" ]] || die "status must be ACTIVE or PAUSED, got '$status'"
    api PUT "/ads/campaigns/${campaignId}/status" "$(jq -n --arg s "$status" '{status:$s}')"
    ;;

  delete-campaign)
    campaignId="${1:?campaignId required}"
    api DELETE "/ads/campaigns/${campaignId}"
    ;;

  duplicate-campaign)
    campaignId="${1:?campaignId required}"; payload="${2:-}"
    if [[ -n "$payload" ]]; then
      [[ -f "$payload" ]] || die "payload not found: $payload"
      api POST "/ads/campaigns/${campaignId}/duplicate" "$(cat "$payload")"
    else
      api POST "/ads/campaigns/${campaignId}/duplicate" "{}"
    fi
    ;;

  bulk-status)
    payload="${1:?payload.json required}"; [[ -f "$payload" ]] || die "payload not found: $payload"
    api POST /ads/campaigns/bulk-status "$(cat "$payload")"
    ;;

  update-ad-set)
    adSetId="${1:?adSetId required}"; payload="${2:?payload.json required}"
    [[ -f "$payload" ]] || die "payload not found: $payload"
    api PUT "/ads/ad-sets/${adSetId}" "$(cat "$payload")"
    ;;

  ad-set-status)
    adSetId="${1:?adSetId required}"; status="${2:?status required (ACTIVE|PAUSED)}"
    [[ "$status" == "ACTIVE" || "$status" == "PAUSED" ]] || die "status must be ACTIVE or PAUSED, got '$status'"
    api PUT "/ads/ad-sets/${adSetId}/status" "$(jq -n --arg s "$status" '{status:$s}')"
    ;;

  create-audience)
    payload="${1:?payload.json required}"; [[ -f "$payload" ]] || die "payload not found: $payload"
    api POST /ads/audiences "$(cat "$payload")"
    ;;

  add-audience-users)
    audienceId="${1:?audienceId required}"; payload="${2:?payload.json required}"
    [[ -f "$payload" ]] || die "payload not found: $payload"
    n=$(jq '.users | length' "$payload" 2>/dev/null || echo 0)
    [[ "$n" -le 10000 ]] || die "add-audience-users: $n users in payload exceeds 10000 cap"
    api POST "/ads/audiences/${audienceId}/users" "$(cat "$payload")"
    ;;

  delete-audience)
    audienceId="${1:?audienceId required}"
    api DELETE "/ads/audiences/${audienceId}"
    ;;

  send-conversions)
    payload="${1:?payload.json required}"; [[ -f "$payload" ]] || die "payload not found: $payload"
    api POST /ads/conversions "$(cat "$payload")"
    ;;

  connect-ads)
    platform="${1:?platform required (facebook|instagram|linkedin|pinterest|tiktok|twitter|googleads)}"
    accountId="${2:-}"
    connect_platform_ok "$platform" || die "connect-ads: bad platform '$platform'"
    api GET "/connect/${platform}/ads$(qs accountId="$accountId")"
    ;;

  help|"")
    grep "^# " "$0" | sed 's/^# //' >&2
    [[ -z "$cmd" ]] && exit 1 || exit 0
    ;;

  *)
    grep "^# " "$0" | sed 's/^# //' >&2
    die "unknown command: $cmd"
    ;;
esac
