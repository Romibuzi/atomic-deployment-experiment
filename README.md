# Atomic deployment experiment

A small experimentation demonstrating this article : http://axialcorps.com/2013/07/03/atomically-replacing-files-and-directories/
in case of deployment of a website.

## The test

The test is composed in two parts.
The first part is `switch-symlink.py` script,
which will constantly change symlink of `current` folder with even `a` or `b` folder
by using a forced (`ln -sfn`) or an atomic (`ln` a temporary link then a `mv`) symlink strategy.

Example :

```bash
# Using atomic strategy
$ python switch-symlink.py atomic
# OR
$ python switch-symlink.py forced
```

The second part consists of simulating HTTP load on the current folder while the `switch-symlink` script is running.

I've used https://github.com/rakyll/boom tool which fits my needs, example :

```bash
$ boom -n 30 -c 2 http://127.0.0.1/atomic-deployment-experiment/current
```


## Results

With atomic strategy :

```bash
$ boom -n 30 -c 2 http://127.0.0.1/atomic-deployment-experiment/current
30 / 30 Booooooooooooooooooooooooooooooooooooooooooooooooooooo! 100.00 %

Summary:
  Total:    0.0815 secs.
  Slowest:  0.0444 secs.
  Fastest:  0.0014 secs.
  Average:  0.0053 secs.
  Requests/sec: 367.9084

Status code distribution:
  [200] 30 responses
```


With forced strategy :

```bash
$ boom -n 30 -c 2 http://127.0.0.1/atomic-deployment-experiment/current
30 / 30 Booooooooooooooooooooooooooooooooooooooooooooooooooooo! 100.00 %

Summary:
  Total:    0.0423 secs.
  Slowest:  0.0078 secs.
  Fastest:  0.0005 secs.
  Average:  0.0026 secs.
  Requests/sec: 709.8952
  Total Data Received:  1806 bytes.
  Response Size per Request:    60 bytes.

Status code distribution:
  [404] 10 responses
  [500] 1 responses
  [200] 19 responses
````

## Conclusion

Both 404 and 500 reponses are problematic in case of forced symlink deployment (`ln -sfn`),
it makes the website unvailable for a short period of time where no symlink is present.
The 500 is even more problematic, it can be the suppression of the symlink (before the replacment by the new)
during a current request, which can leave your application in a very unstable state, e.g an `include()` or an `fopen()` operation.

Solution : Use linux rename operation : `mv` (`os.rename()` in Python), which is an atomic operation, you won't loose your requests using this strategy.
