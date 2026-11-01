# OpenGluon integration

OpenGluon places this engine at `engines/anaxia` as a Git submodule. The engine retains its package, tests, history and MIT license. Quantumlib and the external mathematical libraries retain their own source trees, histories and licenses. Including a source checkout does not mean its dependencies have been installed or its theorems rechecked.

The new commands are:

```sh
anaxia portfolio seed
anaxia portfolio Lehmer
anaxia routes Yang-Mills
anaxia certify examples/rational-psd.json
```

The portfolio is a source snapshot, not a list of independently certified closures. Construction routes expose the assumptions and a failure test. The rational matrix command is an executable exact finite certificate check. Existing engine verification and release gates remain in place.

Project maintainer and author of the new integration material: Deep Bhattacharjee. Original paper authors and third-party software contributors retain their original attribution.
