<h1 align="center">tinyio</h1>
<h2 align="center">A tiny (~300 lines) event loop for Python</h2>

_Ever used `asyncio` and wished you hadn't?_

`tinyio` is a dead-simple event loop for Python, born out of my frustration with trying to get robust error handling with `asyncio`. (I'm not the only one running into its sharp corners: [link1](https://sailor.li/asyncio), [link2](https://lucumr.pocoo.org/2016/10/30/i-dont-understand-asyncio/).)

This is an alternative for the simple use-cases, where you just need an event loop, and want to crash the whole thing if anything goes wrong. (Raising an exception in every coroutine so it can clean up its resources.)

```python
import tinyio

def slow_add_one(x: int):
    yield tinyio.sleep(1)
    return x + 1

def foo():
    four, five = yield [slow_add_one(3), slow_add_one(4)]
    return four, five

loop = tinyio.Loop()
out = loop.run(foo())
assert out == (4, 5)
```

- Somewhat unusually, our syntax uses `yield` rather than `await`, but the behaviour is the same. Await another coroutine with `yield coro`. Await on multiple with `yield [coro1, coro2, ...]` (a 'gather' in asyncio terminology; a 'nursery' in trio terminology).
- An error in one coroutine will cancel all coroutines across the entire event loop.
    - If the erroring coroutine is sequentially depended on by a chain of other coroutines, then we chain their tracebacks for easier debugging.
    - Errors propagate to and from synchronous operations ran in threads.
- Can nest tinyio loops inside each other, none of this one-per-thread business.
- Ludicrously simple. No need for futures, tasks, etc. Here's the entirety of the day-to-day API:
    ```python
    tinyio.Loop
    tinyio.run_in_thread
    tinyio.sleep
    tinyio.CancelledError
    ```

## Installation

```
pip install tinyio
```

## Documentation

### Loops

Create a loop with `tinyio.Loop()`. It has a single method, `.run(coro)`, which consumes a coroutine, and which returns the output of that coroutine.

Coroutines can `yield` four possible things:

- `yield`: yield nothing, this just pauses and gives other coroutines a chance to run.
- `yield coro`: wait on a single coroutine, in which case we'll resume with the output of that coroutine once it is available.
- `yield [coro1, coro2, coro3]`: wait on multiple coroutines by putting them in a list, and resume with a list of outputs once all have completed. This is what asyncio calls a 'gather' or 'TaskGroup', and what trio calls a 'nursery'.
- `yield {coro1, coro2, coro3}`: schedule one or more coroutines but do not wait on their result - they will run independently in the background.

You can safely `yield` the same coroutine multiple times, e.g. perhaps four coroutines have a diamond dependency pattern, with two coroutines each depending on a single shared one.

### Threading

Blocking functions can be ran in threads using `tinyio.run_in_thread(fn, *args, **kwargs)`, which gives a coroutine you can `yield` on. Example:

```python
import time, tinyio

def slow_blocking_add_one(x: int) -> int:
    time.sleep(1)
    return x + 1

def foo(x: int):
    out = yield [tinyio.run_in_thread(slow_blocking_add_one, x) for _ in range(3)]
    return out

loop = tinyio.Loop()
out = loop.run(foo(x=1))  # runs in one second, not three
assert out == [2, 2, 2]
```

### Sleeping

This is `tinyio.sleep(delay_in_seconds)`, which is a coroutine you can `yield` on.

### Error propagation

If any coroutine raises an error, then:

1. All coroutines across the entire loop will have `tinyio.CancelledError` raised in them (from whatever `yield` point they are currently waiting at).
2. Any functions ran in threads via `tinyio.run_in_thread` will also have `tinyio.CancelledError` raised in the thread.
3. The original error is raised out of `loop.run(...)`. This behaviour can be configured (e.g. to collect errors into a `BaseExceptionGroup`) by setting `loop.run(..., exception_group=None/False/True)`.

This gives every coroutine a chance to shut down gracefully. Debuggers like [`patdb`](https://github.com/patrick-kidger/patdb) offer the ability to navigate across exceptions in an exception group, allowing you to inspect the state of all coroutines that were related to the error.

### Batteries-included

We ship batteries-included with the usual collection of standard operations.

<details><summary>Click to expand</summary>

```python
tinyio.as_completed       tinyio.Semaphore
tinyio.Barrier            tinyio.ThreadPool
tinyio.Event              tinyio.timeout
tinyio.Lock               tinyio.TimeoutError
```

---

- `tinyio.as_completed({coro1, coro2, ...})`

    This schedules multiple coroutines in the background (like `yield {coro1, coro2, ...}`), and then offers their results in the order they complete.

    This is iterated over in the following way, using its `.done()` and `.get()` methods:
    ```python
    def main():
        iterator = yield tinyio.as_completed({coro1, coro2, coro3})
        while not iterator.done():
            x = yield iterator.get()
    ```

---

- `tinyio.Barrier(value)`

    This has a single method `barrier.wait()`, which is a coroutine you can `yield` on. Once `value` many coroutines have yielded on this method then it will unblock.

---

- `tinyio.Event()`

    This is a wrapper around a boolean flag, initialised with `False`.
    This has the following methods:
    
    - `.is_set()`: check the value of the flag.
    - `.set()`: set the flag to `True`.
    - `.clear()`: set the flag to `False`.
    - `.wait()`, which is a coroutine you can `yield` on. This will unblock if the internal flag is `True`. (Typically this is accomplished by calling `.set()` from another coroutine or from a thread.)

---

- `tinyio.Lock()`

    This is just a convenience for `tinyio.Semaphore(value=1)`, see below.

---

- `tinyio.Semaphore(value)`

    This manages an internal counter that is initialised at `value`, is decremented when entering a region, and incremented when exiting. This blocks if this counter is at zero. In this way, at most `value` coroutines may acquire the semaphore at a time.

    This is used as:
    ```python
    semaphore = Semaphore(value)

    ...

    with (yield semaphore()):
        ...
    ```

---

- `tinyio.timeout(coro, timeout_in_seconds)`

    This is a coroutine you can `yield` on, used as `output, success = yield tinyio.timeout(coro, timeout_in_seconds)`.
    
    This runs `coro` for at most `timeout_in_seconds`. If it succeeds in that time then the pair `(output, True)` is returned . Else this will return `(None, False)`, and `coro` will be halted by raising `tinyio.TimeoutError` inside it.

---

- `tinyio.ThreadPool(max_threads)`

    This is equivalent to making multiple `tinyio.run_in_thread` calls, but will limit the number of threads to at most `max_threads`. Additional work after that will block until a thread becomes available.

    This has two methods:

    - `.run_in_thread(fn, *args, **kwargs)`, which is a coroutine you can `yield` on. This is equivalent to `yield tinyio.run_in_thread(fn, *args, **kwargs)`.
    - `.map(fn, xs)`, which is a coroutine you can `yield` on. This is equivalent to `yield [tinyio.run_in_thread(fn, x) for x in xs]`.
 
---

</details>

## FAQ

<details>
<summary>Why <code>yield</code> - why not <code>await</code> like is normally seen for coroutines?</summary>
<br>

The reason is that `await` does not offer a suspension point to an event loop (it just calls `__await__` and maybe *that* offers a suspension point), so if we wanted to use that syntax then we'd need to replace `yield coro` with something like `await tinyio.Task(coro)`. The traditional syntax is not worth the extra class.
</details>

<details>
<summary>I have a function I want to be a coroutine, but it has zero <code>yield</code> statements, so it is just a normal function?</summary>
<br>

You can distinguish it from a normal Python function by putting `if False: yield` somewhere inside its body. Another common trick is to put a `yield` statement after the final `return` statement. Bit ugly but oh well.
</details>

<details>
<summary>vs <code>asyncio</code> or <code>trio</code>?.</summary>
<br>

I wasted a *lot* of time trying to get correct error propagation with `asyncio`, trying to reason whether my tasks would be cleaned up correctly or not (edge-triggered vs level-triggered etc etc). `trio` is excellent but still has a one-loop-per-thread rule, and doesn't propagate cancellations to/from threads. These points inspired me to try writing my own.

`tinyio` has the following unique features, and as such may be the right choice if any of the following are must-haves for you:

- the propagation of errors to/from threads;
- no one-loop-per-thread rule;
- simple+robust error semantics (crash the whole loop if anything goes wrong);
- tiny, hackable, codebase.

However conversely, `tinyio` does not offer the ability to schedule work on the event loop whilst cleaning up from errors.

If none of the bullet points are must-haves for you, or if needing the event loop during cleanup is a dealbreaker, then either `trio` or `asyncio` are likely to be better choices. :)

</details>
