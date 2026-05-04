---
source: reddit
workspace: personal
ingested_at: "2026-05-04T21:51:01.042227+00:00"
ingest_version: 1
content_hash: "sha256:cccd87b328ca6bdb782b3ba3a9e416126b319c39d5078e123939e0b9eff7a46c"
provider_modified_at: "2026-04-28T00:58:25+00:00"
post_id: 1sxmg6z
permalink: "https://reddit.com/r/Python/comments/1sxmg6z/pep_661_sentinel_values_has_been_accepted_for/"
url: null
subreddit: Python
author: u/M_V_Lipwig
title: PEP 661 (Sentinel Values) has been accepted for release in 3.15!
flair: News
score: 294
num_comments: 117
upvote_ratio: 0.95
nsfw: false
spoiler: false
locked: false
top_comments_captured: 30
max_depth_captured: 6
---
# PEP 661 (Sentinel Values) has been accepted for release in 3.15!

> r/Python · u/M_V_Lipwig · 294↑ · 117c · 6d · [News]
> https://reddit.com/r/Python/comments/1sxmg6z/pep_661_sentinel_values_has_been_accepted_for/

## Selftext

After five years of discussion, [PEP 661](https://discuss.python.org/t/pep-661-sentinel-values/9126/337), which adds support for sentinel values, has been accepted and is due for a release in 3.15. The use case is relatively simple:

    MISSING = sentinel('MISSING')
    
    class Logger:
    def __init__(self, level:MISSING|None|str = MISSING):
      if level is MISSING:
        self.level = get_global_default_level()
      else:
        self.level = level

There are 3 possible outcomes that can be handled by this pattern

1. If no argument was provided, use the default
2. If None is passed, disable logging
3. If a level is passed, use it

The important thing here is a specific way to check if *any* argument was provided to the function, vs a caller propagating a None to it. The ability to check if an argument was actually provided by the caller was a great feature I liked in FORTRAN, so it's nice that it's made it to python!

## Top 50 comments (depth 6)

- **u/Original-Ad-4606** (233↑): I’m not sure what all the hate is about.  I for one have had many situations where None actually means something and have needed to create my own implementation of a Sentinel value to tell the difference between None and the user simply not providing a value.
  
  Many libraries have had to implement Sentinels internally… Pandas and Pydantic come to mind.
  
  I welcome this feature!
  - **u/M_V_Lipwig** (72↑): I didn't expect people to get so pissed lol. Btw if you're pissed, go read the 300 comment long PEP discussion which answers most of your questions!
    
    But then again, I suppose that's the reason it took five years to get out of PEP hell! Hopefully null-coalescing operators is the next PEP to get out...
    - **u/binaryfireball** (8↑): dont get me wrong, im not angry nor do I hate it.  its just a meh really
    - **u/ConcreteExist** (1↑): The or operator basically functions as null-coalescing operator already.
      - **u/M_V_Lipwig** (8↑): 1. Semantically confusing (are you actually checking for truthiness or "noneiness"?)
        2. Sounds good until your None-ish type has \_\_bool\_\_ disabled...
    - **u/Jason-Ad4032** (1↑): I think Python could just implement this as a class method on `None` and `sentinel`.
      
      ```
      c = None.coalescing(a, b)        # c = a ?? b
      c = MISSING.coalescing(a, b)     # c = b if a is MISSING else a
      None.coalescing_attr(a).b   # a?.b
      ```
      
      The meaning is very clear, and it would be easy to document. It just needs an appropriate name.
      - **u/M_V_Lipwig** (0↑): Why is the meaning of a ?? b any less clear than a && b? Imagine you are coming into programming for the first time. How are the two any different in terms of mental complexity? You're just used to seeing a && b so your mind accepts it as obvious, while you aren't used to a ?? b so your mind goes "zomg so complex".
        - **u/Jason-Ad4032** (1↑): It’s not harder to understand. 
          
          The issue is that once you introduce a sentinel, you’d still need something like `c = b if a is MISSING else a`, because `??` only applies to `None`.
          
          If you’re worried that a function can’t short-circuit, then use a ternary expression. If you’re concerned about the learning cost of symbols, then use a keyword.
          
          What I don’t understand is why, after introducing a sentinel, you would still give special treatment only to `None`, when the same operation clearly appears in the sentinel example.
          
          By the way, your reply makes it seem like you’re not really reading what others are saying. please at least try to understand their point.
    - **u/danted002** (-3↑): null-coalescing operators make sense in some languages, I’m not sure it makes sense in Python. If you want to pluck values from nested objects you have pattern matching which is more readable or just access them directly and wrap the statement with a try … except KeyError …. Better yet use Pydantic to properly parse your input and default the value to None. 
      
      Every time I user it it TS there was an if later down the line which would be solved by pattern matching in python
      - **u/M_V_Lipwig** (7↑): You do realize how much more elegant and readable
        
        a?.b 
        
        is over 
        
        a.b if a is not None else None
        
        right? Also, "use a third party package for a language feature" is not an appropriate solution.
        - **u/danted002** (1↑): match a:
             case A(b=type_of_b(b))
                 do_something_with_(b)
             case _:
                 # we fucked up so fail gracefully 
          
          
          Is about 10000 times more sound then a?.b where we know fuck all about a or b. Also what would the operator look like in index operations a?[“b”]?
          - **u/M_V_Lipwig** (1↑): First off, in python you have no actual certainty on what a is. It could be anything! So I don't get what you mean by soundness. This isn't C++. 
            
            Second, If you want to set c:type(b) | None, currently you need to do 
            
              
            c: type(b) | None = None if a is not None else a.b
            
              
            c = a?.b is very, very simple and elegant syntax. 
            
              
            \> Also what would the operator look like in index operations a?\[“b”\]?
            
            Sure, why not? Anyway, the null-coalescence PEP has been split up into multiple parts, so perhaps null-coalesced indexing may never make it into the language. It's not all or nothing.
            - **u/danted002** (1↑): apparently isinstance and type checking in the pattern matching have been removed from the language and type introspection became impossible.
              
              Regarding your example you can literally use the pattern matching example I gave to write c = b in an elegant descriptive way.
              
              The null operator will invite even more crappy code (see TypeScript) in codebase but then again, everyone is just regurgitating LLM slop in their PRs so why even bother anymore.
        - **u/Effective-Total-2312** (1↑): something = None
              if some_object is not None:
                  something = some_object.some_attr
  - **u/denehoffman** (26↑): Yeah, the hate is goofy, I’ve had so many situations where I’ve needed sentinels (fitting algorithms where None disables a termination method but Default uses the default, for example). The complaints about cluttering the language are silly, it’s a new builtin, a single function!
    - **u/QuasiEvil** (3↑): I'm just a hobby programmer and I run into this pattern all the time. Super excited for this!
    - **u/No_Flounder_1155** (1↑): because its an api choice and not a need...
      
      OPs design choice for logging is a really poor example justifying this and a good example of bad api design choice.
      
      It literally overloads value selection and control flags.
      
      Like why would you want to set a log level and its side effect is to disabling logging?
      - **u/BogdanPradatu** (6↑): Yeah, I was reading the logging example and wasn't able to see why I would ever do that.
        - **u/denehoffman** (2↑): Sure it’s not the best example, but imagine a field where None has a meaning other than “default” or “not specified”. Matplotlib is a great example of this taken to silly extremes, there are many keywords arguments where None, “none”, and “” all have different behavior, and this ambiguity could easily have been fixed by sentinel values.
          - **u/wunderspud7575** (13↑): I don't disagree with your general point, but leaning on matplotlib, the most pathological API known to mankind, to illustrate your point did raise a chuckle.
            - **u/denehoffman** (2↑): They honestly need to just do a major version bump and completely break the API at this point. But I had to give an example people were familiar with, and it’s a very commonly used pathological API!
      - **u/denehoffman** (5↑): The use case seems pretty obvious, you let the user disable logging by passing None to some  logger constructor. 
        
        The real issue is not the “None” turning off logging, it’s that None semantically means “nothing” or “null” so expecting the behavior of passing None to give the default logger doesn’t make any sense. A sentinel value is basically just a replacement for None that has meaning. As I mentioned, a Default sentinel is often very useful when None actually should mean disabling things.
        
        But to the bigger complaint of “it’s an api choice and not a need”: so is the use of “None” in the first place. It’s python, we could force users to make up marker types to represent optional state, but because lots of API choices deem this ugly, we don’t do it. If you didn’t care about making nice APIs and only focused on what is needed to write code, then there is a whole world of Turing-complete ways to do this, they’re just ugly. At the end of the day, we should welcome features that make code more readable and writable, and this does that without any major impact if you don’t want to use it.
        - **u/No_Flounder_1155** (-1↑): way to not even understand the point.
          - **u/denehoffman** (2↑): I understand your point just fine, OP’s example isn’t a good one, but that doesn’t mean there aren’t legitimate use cases where the alternative would be more verbose or confusing.
            - **u/No_Flounder_1155** (-1↑): ugly is not a fact, but opinion. I asked why this was needed and you respond with "its ugly to not do it this way"....
      - **u/treasonousToaster180** (3↑): alternative example then:
        
            class SomeWebAPIClass:
              
              def get_json_data(default: MISSING|Any = MISSING) -> dict:
                try:
                  # some logic here to fetch data from a web api
                except ConnectTimeout as e:
                  if default is MISSING:
                    raise APIUnreachableError()
                  return default
        
        In this example, the `default` param is used in case of any kind of error when provided, and raises exceptions when it isn't and the data cannot be retrieved/parsed.
        
        This would be useful in a situation where we periodically fetch data for updating constants or configurations, and if we are unable to fetch we can simply continue to use our existing values (even when that value is None), but also want to fail at the start if no value is provided:
        
            class SomeConfigurationClass:
              
              @property
              def api(self):
                if (api:=getattr(self, '_api', None)) is None:
                  setattr(self, '_api', api:=SomeWebAPIClass())
                return api
            
              def __init__(self):
                self.web_config = self.api.get_json_data()
            
              def _update_config(self):
                self.web_config = self.api.get_json_data(default=self.web_config)
        
        This also may not be the most practical example, but it catches the broad idea and I have seen other cases where passing `None` into a method had a specific meaning (usually "return to default state") that had to use a special constant created on runtime to use as a placeholder for when *no* value was provided.
        - **u/Effective-Total-2312** (2↑): This is very interesting, but in all honesty (and just a comment, don't feel attacked), I dislike any code that uses Any, dict (alone or with primitives), or tuple (alone or with primitives), so any new feature that encourages the use of these, I am biased to not like it (I don't even like too much None to begin with, but it has its fair amount of use cases to me).
  - **u/WildCard65** (6↑): attrs also has its own sentinel as well
  - **u/nicholashairs** (3↑): Yup I also have a need for this feature 💪💪💪
  - **u/IAmASquidInSpace** (1↑): CHANGE BAD! ME NO LIKE CHANGE! /s
    
    
    Seriously though, this is a feature I've needed a few times in the past, where `None` had a meaning other than "no value provided", and every time I ended up with some hacky `object` or `enum` trick and staring longingly at PEP 661. Finally having this in is great!
  - **u/memesearches** (1↑): Airflow is another
  - **u/jessekrubin** (1↑): Ellipsis?
- **u/aloobhujiyaay** (70↑): this is way better than using object() hacks everywhere, readability and intent improve a lot
  - **u/Ph0X** (12↑): from an API user, how is `MISSING = object()` different from `MISSING = sentinel()`?
    
    From a contributor point of view, a simple comment above the former saying `This is a sentinel value` does basically the same, no?
    - **u/sphen_lee** (37↑): Type checkers work better if the sentinel has a type specific to itself, whereas all `objects` are the same type
    - **u/fiddle_n** (24↑): The PEP gives a few drawbacks to using object:
      
      * object has a very long and verbose repr by default
      * You can’t really type hint sentinels using object properly
      * You can’t check if one sentinel is equal to another if you need to copy it
      
      Top two affects API users, I would say.
    - **u/Brian** (1↑): Type annotations are a problem with just object.  If you annotate it as `ExpectedType | object`, you're basically allowing anything - there's no real equivalent to `Literal[]` for arbitrary sentinels.  
      
      I've taken to doing something like:
      
          class Missing:
              value: ClassVar[Missing]
      
              def __repr__(self): ... # Provide a bit more meaningful repr
      
          Missing.value = Missing()
      
      And then `def myfunc(x : str | Missing = Missing.value):...`.  But I prefer the new approach for reducing the boilerplate here, and making it clearer that it's a singleton instance being used (eg. you have to use `isinstance(x, Missing)` rather than just `x is Missing.value` to have type checkers narrow the type correctly).  Also makes things a bit more standardised: there's lots of code out there using subtly different methods, so having one obvious way to do it should result in more consistency.
  - **u/IcecreamLamp** (1↑): Can also use `unittest.mock.sentinel` lol
- **u/el_extrano** (37↑): Pedantic point, but the PRESENT intrinsic to test whether an argument was supplied is only available in Fortran 90 and later, so you can't say it's from "FORTRAN": the all caps spelling is only for the 77 standard and earlier!
  - **u/M_V_Lipwig** (10↑): You'll have to pry all caps spelling from my cold dead hands!
- **u/binaryfireball** (31↑): i guess it's nice but tbh i dont feel like the benefits outweigh cluttering the language with even more features. One of the things I like about python is that  its fairly idiomatic in the sense that there is one(or a couple) generally accepted way to do things. Pergaps I dont work in the same domain as you but the amount of times ive had to worry about this issue is negligible.
  
  edit: im pretty sure you could achieve the same thing with a constant passed as default or at least in cases where theres not a ton of args
  - **u/ottawadeveloper** (27↑): I've seen a number of libraries use the Ellipsis to do this, eg
    
    
    ```
    def func(arg: str = ...): ...
    ```
    
    
    The downside is strict typing requires this. to actually be:
    
    
    ```
    def func(arg: str | types.EllipsisType = ...):
      if arg is ...:
        arg = 'default'
    ```
    
    
    And then the type checkers start complaining that `EllipsisType` isn't a string even though you changed it to a string (which may be a bug in my PyCharm for 3.14 since it's pretty clearly not ever an Ellipsis after the if statement). It doesn't like retyping variables either, so I end up with the ugly `real_arg = 'default' if arg is ... else arg`.
    
    
    Anyways, that aside, there's a lot of value for this. If you read the PEP, the current best practice to make one (even in the standard library) is `empty = object()`. But that creates weird issues if you copy or pickle it, especially if you use `is` instead. `None` is available and works most of the time but not always. And `...` isn't supposed to be a placeholder even though the datetime module uses it plus you have to use EllipsisType rather than ... in the type hint (unlike None which works in type hints). 
    
    
    It would be a lot cleaner to be able to define a sentinel value that works well, can be used in type hints, and can be pickled properly. Nice to see this used.
    - **u/Effective-Total-2312** (2↑): Wouldn't using an Enum and/or a switch case be much better in that scenario ? "None" is not semantic if it intends to mean something, and the exact source of this PEP is exactly that "it may not exactly be None but a missing argument", then why not have an explicit argument ?
      
      I mean, it's in the zen of python.
      - **u/M_V_Lipwig** (16↑): Consider reading the PEP...
        - **u/Effective-Total-2312** (1↑): Will definitely do when possible ! I appreciate a lot the work behind the scenes of people in Python, don't get me wrong on my comments
      - **u/ottawadeveloper** (3↑): An enum with one value seems silly, but I guess you could. You could consider sentinel a one valued enum.
        
        
        I personally don't like to use None other than "this thing wasn't set" but I've seen valid use cases - the best example is `inspect.empty` which is used for `parameter.default` when inspecting a function. Since a value of None is a valid default, then distinguishing between a default of None and no default provided requires a trick like this. 
        
        
        Another decent example is datetime.replace() which takes keyword arguments and uses "..." to indicate that a value shouldn't be replaced. This is necessary because having a `tzinfo` of None is relevant (it means it's naive) and so passing tzinfo=None could be confusing. 
        
        
        Really `value: TYPE | None = None` should cover many uses for most programmers, but there is definitely a need beyond that
        - **u/Effective-Total-2312** (1↑): Not what I meant. If you have an argument, that means you have a finite number of values you expect to accept; those should be your type. If your type requires a conjunction with another type (None for example) I already find that not so good (but using "| None" is a convenient mechanism to have optional arguments/values).
          
          I am truly failing to see any need to have something else, unless you are expecting very messy use of your API upstream, which I think you should not do but rather force your consumers to follow specific data structures (similar to what Pydantic did changing from v1 to v2 with ConfigDict).
  - **u/M_V_Lipwig** (25↑): The PEP addresses this here: [https://peps.python.org/pep-0661/#add-a-single-new-sentinel-value-such-as-missing-or-sentinel](https://peps.python.org/pep-0661/#add-a-single-new-sentinel-value-such-as-missing-or-sentinel)
    
    Edit: Also the point of this PEP is that there were a couple of terrible ways of doing this already, each of which had some serious problems - especially with type checking! I encourage you to read the original PEP post on this reddit, the first comment of which is "I don't think people in the comments understand how important type checking is going to be".
    
      
    So the point of the PEP is to provide the idiomatic solution. Of course, users can go around the idiom and write terrible code, but now they have no excuse ;)
  - **u/tobsecret** (24↑): The whole point is to establish one clear way to implement sentinels. There were many bad ways of doing it, including the bad way you're suggesting. 
    
    
    This is a good addition to the language. If you need a sentinel value, use sentinel.
    Not every pep has to introduce massive changes.
    - **u/NuclearFoodie** (10↑): Yeah but this just clutters the language, maybe if they took something out to prevent language clutter, maybe classes or something /s
      
      Sorry, my annoyance at the bs  clutter argument needed a snarky outlet.
      - **u/Daishiman** (1↑): It _doesn´t_ clutter the language. It removes various mutually incompatible conventions with a single, standardized convention that's trivial to refactor.
        - **u/NuclearFoodie** (1↑): r/whoosh
- **u/TMiguelT** (22↑): Isn't your example incorrect? You have `level=MISSING|None|str` but I think you mean `level: MISSING|None|str = MISSING` no? On my first reading I thought this was a bizarre change to how the `|` operator worked but I now realise that this PEP only adds `sentinel` (which admittedly is handled specially by the type system).
  - **u/M_V_Lipwig** (15↑): Hah you're right! that's what happens when you code without an IDE lol
- **u/teerre** (19↑): Anything but imponent real enums lol
- **u/Uncle_DirtNap** (20↑): This is GREAT NEWS, and haters have to get over it, this is super useful.
  - **u/Paddy3118** (3↑): Please add examples of your own.
    - **u/BossOfTheGame** (12↑): I think the best example is a dict-like get method with a default parameter that you can use with keyword args. if you don't specify the default it should error if it is a key error, otherwise it should return the default, and None is a very valid default value. This is exactly the case I wrote ubelt.NoParam for.
    - **u/HEROgoldmw** (2↑): Think about your a custom configuration library.
      This configured value, is allowed to be None or int.
      
      Now add a feature, where you warn users of unconfigured config values. You can NOT do that using None, as None is a valid value.
      Thats why where you have an internal use only, default sentinel value named MISSING.
      Now you know if the config is empty, or set to None.
      Without sentinels, there's practically no (even remotely easy) solution for the feature.
- **u/Marksta** (12↑): Love it, I feel like Python has already been so wobbily on wtf None is way more than other languages are with their NULL/VOID etc types. None isn't actually nothing, it has meaning all over the place. Especially with the truthy-falsey stuff. Giving a formal way to discern the implicit None and an explicit None seems like a good move to me.
- **u/Trang0ul** (8↑): >Note: Changing all existing sentinels in the stdlib to be implemented this way is not deemed necessary, and whether to do so is left to the discretion of the maintainers.
  
  Why not? If this is the new “official” pattern, the stdlib should lead by example. Otherwise it’s just another optional idiom, not a standard.
  - **u/SlinkyAvenger** (3↑): That would require a major version change
- **u/tobsecret** (7↑): I like this. When it comes up, it's nice to have a prebuilt solution that has considered the common edge cases already.
- **u/Orio_n** (7↑): Whats wrong with an enum?
  - **u/tunisia3507** (10↑): Because you can't load arbitrary data into an enum (missing OR None OR int).
    - **u/xfunky** (1↑): I think he meant something like this (notice that Guido himself suggested this method)
      
      
      ```
      class Empty(enum.Enum):
         token = 0
      
      _empty = Empty.token
      
      def my_func(val: int | None | Empty = _empty):
          …
      ```
      
      
      [https://github.com/python/typing/issues/236#issuecomment-227180301](https://github.com/python/typing/issues/236#issuecomment-227180301)
- **u/mpersico** (8↑): Named arguments and just don’t pass it. For a language that was supposed to be so simple the amount of stuff that’s being piled on makes it look like C++.
- **u/No_Flounder_1155** (7↑): I don't think the logging example is very good. Why should None stop logging from working. Seems really weird.
  - **u/Marksta** (1↑): I'm imagining the use case is you're calling some other code that is going to call log() statements, so you must have a logger object so just not initiating it isn't the solution. If you want the logger totally disabled but you are going to initialize it, then I guess usual options is to set it to something like loglevel=FATAL where hopefully it goes un-used, set its output to null but maybe this has performance impact that it's still doing something for each log statement, or hope the logger implementation already has a "None" option somehow, somewhere, which really doesn't have a simple pattern for that right now to my knowledge. Sounds like setting log level to None to me would be the right pattern.
    
    So for the logger example, the question is would you expect log = Logger(), log.info() to just print nothing? I'd personally assume a no param Logger() object has some sort of defaults that include logging, but a Logger(loglevel=None) and it checking to see that I actually wanted the nothing burger Logger object makes way more sense.
    
    But should a Logger() object with no parameters really just be a disabled logger? Probably not, thus this PEP.
    - **u/No_Flounder_1155** (3↑): you could always just have disabled=True. That gets rid of magical side effects.
- **u/caprine_chris** (5↑): This is amazing.
- **u/dusktreader** (3↑): FINALLY.
- **u/spinwizard69** (3↑): Things like this lead me to actually believe we need to bring back mental health prisons (Hospitals) and heavily applied ECT.    What the hell are these people up to, trying to turn Python into C++?    Pretty soon people will find themselves reading every program line in a Python program several times just to figure out what it is doing.   idiomatic Python died today.
- **u/samettinho** (1↑): Honestly, I've never needed this before and I can't really see the benefit; maybe something very minute.
  - **u/denehoffman** (2↑): My use case is an optimization library with config object. This object contains arguments which represent algorithm terminator configurations, which are themselves objects. If the user specifies None for one of these terminators, the interpretation is that that terminator isn’t included in the algorithm loop. Omitting the argument would imply the default terminator. A “missing/default” sentinel is an easy choice, and I ended up writing my own code which could be replaced by a single line now.
    
    Could I have rewritten the entire library such that terminators each come with an enabled/disabled Boolean flag? Sure, it would have been even more work, and the underlying code is a Rust library so I’d have to rewrite the bindings for that too. Sentinels just simplify that decision while being invisible to the user, except when they read type hints or documentation, they’ll see “default” instead of “None” and not get confused as to what “None” does.
    
    This extends to any code where “None” has a different semantic meaning than “default” or “missing”.
    - **u/samettinho** (1↑): Basically, instead of two variables, you can use a single one: `variable, is_variable_enabled`
      
      
      If my understanding is correct, it is a valid case but unless you have a scenario where you have several of these, it is a small one.
      - **u/denehoffman** (1↑): Yes, it’s a bit niche, but so are a lot of the language concepts that people rarely use on a day-to-day basis. I hardly ever write metaclasses or decorators outside of the niche situations where I need one that isn’t already written by the stdlib or some other package
- **u/eztab** (2↑): was there any problem in just using a class for this? I do have this situation where I need another sentinel since None is taken already and just used a class (that does nothing).
- **u/Dull-Researcher** (2↑): Excellent for default immutable values or placeholders for the same, when None has a different meaning.
- **u/IcecreamLamp** (2↑): I prefer the syntax of `unittest.mock.sentinel` over this
- **u/jimanri** (2↑): I dont get it. to me this just looks like and invisible if, since the None case is do nothing and yet is not explicit.
- **u/llun-ved** (2↑): How is this appreciably different than:
  
  sentinel = object()
  
  def fn(myarg = sentinel):
    if myarg is sentinel: whatever. 
  
  I’ve used these for years without issue.
  - **u/uselessbaby** (1↑): One major one for me is annotations, you can do fn(myarg: sentinel|None|int=sentinel) for instances where None might have its own meaning
    - **u/llun-ved** (1↑): This can be done with a class. Seems odd to extend the language for a typing convenience, but I agree it will make it easier and more clear.
- **u/UltraPoci** (1↑): Can't we just use EllipsisType?
- **u/denehoffman** (1↑): Another example:
  
  ```python
  
  UNSET = sentinel("UNSET")
  
  def connect(timeout=UNSET):
      if timeout is UNSET:
          timeout = get_default_timeout()
      elif timeout is None:
          timeout = None  # explicitly disable timeout
      return _connect(timeout=timeout)
  ```
  
  Adding an argument like `no_timeout: bool’ is semantically confusing and allows for unused state in the signature (`connect(timeout=30, no_timeout=True)`).
  
  Why can’t you just use `object()` for the sentinel? Well for one, it doesn’t serialize, so if you wanted to store some user settings without storing the default (for example, you want to store the fact that the user didn’t set the value but allow the default to change in future versions), you’d have trouble. It also doesn’t play well with type hints, since it just has a type of object.
- **u/OkTrack9724** (1↑): u/AskGrok please explain me that like I'm a HTML programmer
- **u/Honest-Estate-4592** (1↑): completely make sense, this is great, I will definitely help the code readability.
- **u/assumptionkrebs1990** (0↑): Nice solution (I would have likely build a provider (sentinel) wrapper class to handel such cases and then fallen into feature creep.)
- **u/RedSinned** (0↑): Ironically I was at PyConDe 2 weeks ago and there was a talk about sentinel values. The talk is not online yet but the slides are: https://pretalx.com/pyconde-pydata-2026/talk/88TTRY/
- **u/BDube_Lensman** (-11↑): The number of cases where `MISSING` and `None` are able to have legitimate differences in semantic meaning has to be likes of cases, and we're added even more crap to the language to cover those.  That's a thumbs down, people should not use this in their code.
- **u/Effective-Total-2312** (-9↑): I don't really understand the benefit. If you use type hints and static type checkers, why would you be doing this kind of thing ? Sounds like a solution to a problem that is only hiding a design issue behind
  - **u/nosjojo** (8↑): This is handy for serializers, where None is a valid object to encode. You want to be able to determine that they actually meant to encode None instead of passing nothing in.
    - **u/sausix** (2↑): Basically every dict.get method when "None" is different from missing.
  - **u/nicholashairs** (7↑): It's very common in libraries where something is acting like a dict and `None` is a valid value to store so you need to distinguish it from missing values.
    
    An example is stdlib contexvars.MISSING https://docs.python.org/3/library/contextvars.html#contextvars.Token.MISSING
    
    I would expect that most users never need to use it or know that they are using it
    - **u/Effective-Total-2312** (-4↑): I kinda don't like it anyway, I think python already has tons of features that would be better than having an argument that could:
      
      \- Have a proper value of a specific type  
      \- Be None  
      \- Be Missing
      
      That's too error prone, and also it's too implicit on the meaning of that argument, which goes against the zen of python of prefering always explicit over implicit.
  - **u/sausix** (4↑): This kind of complexity is more focussed on developing tools and toolkits. It may look obsolete for end user applications.

## External links cited in comments

- https://peps.python.org/pep-0661/#add-a-single-new-sentinel-value-such-as-missing-or-sentinel
- https://github.com/python/typing/issues/236#issuecomment-227180301
- https://pretalx.com/pyconde-pydata-2026/talk/88TTRY/
- https://docs.python.org/3/library/contextvars.html#contextvars.Token.MISSING
