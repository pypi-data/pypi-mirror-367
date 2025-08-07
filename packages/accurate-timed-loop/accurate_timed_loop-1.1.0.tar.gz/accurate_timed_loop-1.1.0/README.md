* website: <https://arrizza.com/python-accurate-timed-loop.html>
* installation: see <https://arrizza.com/setup-common.html>

## Summary

This is a python module that provides a way to have an accurate timed loop.

For example if you need to do an activity every 250ms +/-10ms, this loop will do that.

## Sample code

see sample.py for a full example

```python
import accurate_timed_loop

loop_delay = 0.250  # seconds
total_wait = 25.0  # seconds
for elapsed, start_time in accurate_timed_loop.accurate_wait(total_wait, loop_delay):
    # ... do task every 250 mS
    pass
```

## Scripts

* See [Quick Start](https://arrizza.com/user-guide-quick-start) for information on using scripts.
* See [xplat-utils submodule](https://arrizza.com/xplat-utils) for information on the submodule.

## Accuracy and Limitations

The sample.py does testing and shows that on Windows MSYS2 the std deviation error is roughly
4mS in a 250mS loop. This means that 95% of loops will be +/-8 mS of the requested loop_delay.

```text
      expected    elapsed  diff1(ms)  actual(s)  diff2(ms)
  1   0.000000   0.000000      0.000   0.000000      0.000
  2   0.250000   0.257294      7.294   0.257294      7.294
<snip>
100  24.750000  24.764093     14.093  24.764093     14.093
101  25.000000  25.015579     15.579  25.015579     15.579


Stats:
loop count     : 101 loops
Error Range    : 0.000 to 24.406 mS
Error Stddev   :      5.009 mS
Error Average  :      8.863 mS
Recommended adj: 0.012200
     sample rc=0
     doit overall rc=0
```

This value is specific to Windows and to the PC that it is running on.

To make it more accurate for your PC and OS use the fixed_adjustment parameter.
Set it so the minimum and maximum are roughly symmetrical around 0.
The Stdev and Average error values at that point should be minimal.

```python
import accurate_timed_loop

loop_delay = 0.250  # seconds
total_wait = 25.0  # seconds
adj = 0.009228  # macOS
for elapsed, start_time in accurate_timed_loop.accurate_wait(total_wait, loop_delay, fixed_adjustment=adj):
    # ... do task every 250 mS
    pass
```

Notes:

* Re-run this several times, and tweak the fixed adjustment.
* The sample.py reports a "Recommended adj" that usually results in better accuracy.
* macOS and Ubuntu tend to be less variant than Windows

This report shows that std deviation is much better.

```text
      expected    elapsed  diff1(ms)  actual(s)  diff2(ms)
  1   0.000000   0.000000      0.000   0.000000      0.000
  2   0.250000   0.251537      1.537   0.251537      1.537
<snip>
101  25.000000  24.989502    -10.498  24.989502    -10.498
102  25.250000  25.241386     -8.614  25.241386     -8.614


Stats:
loop count     : 102 loops
Error Range    : -9.228 to 5.864 mS
Error Stddev   :      1.238 mS
Error Average  :      4.953 mS
Recommended adj: 0.009228
     sample rc=0
     doit overall rc=0
```

Limitations:

* there is NO guarantee that the average error will always be that low or that consistent
* the following runs were on a macOS

```text
# === first run:
Stats:
loop count     : 102 loops
Error Range    : -9.486 to 4.613 mS
Error Stddev   :      1.962 mS
Error Average  :      5.775 mS
Recommended adj: 0.009486

# === second run:
Stats:
loop count     : 102 loops
Error Range    : -9.587 to 3.287 mS
Error Stddev   :      2.163 mS
Error Average  :      6.745 mS
Recommended adj: 0.009587

# === third run:
Stats:
loop count     : 102 loops
Error Range    : -9.472 to 6.782 mS
Error Stddev   :      1.546 mS
Error Average  :      5.597 mS
Recommended adj: 0.009472

# === fourth run:
Stats:
loop count     : 101 loops
Error Range    : -9.518 to 10.365 mS
Error Stddev   :      1.865 mS
Error Average  :      5.410 mS
Recommended adj: 0.009518

# === fifth run:
Stats:
loop count     : 101 loops
Error Range    : -9.369 to 13.726 mS
Error Stddev   :      2.196 mS
Error Average  :      5.614 mS
Recommended adj: 0.009369
```

* if you use the adj parameter the incoming "elapsed" parameter will not be after your expected delay.
  For example these two came in:
    * at 24.749 seconds instead of the expected 24.750 seconds
    * at 24.999 seconds instead of the expected 25.000 seconds

```text
      expected    elapsed  diff1(ms)  actual(s)  diff2(ms)
100  24.750000  24.749573     -0.427  24.749573     -0.427
101  25.000000  24.999601     -0.399  24.999601     -0.399
```
