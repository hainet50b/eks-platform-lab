# eks-platform-lab

How to build a just-enough application platform on
[Amazon EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html)
with an AI coding agent and its skills from the
[Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/what-is-agent-toolkit.html)
and [APEX Skills](https://aws-samples.github.io/sample-apex-skills/), in
numbered, rebuildable parts.

## Overview

This repository is split into numbered parts under `parts/`.

```
┌─ 00 aws-account ──────────────────────────────┐
│                                               │
│   AWS account                                 │
│                                               │
└───────────────────────────────────────────────┘
```

## Parts

A part holds two kinds of content: configuration files and scripts, and
instructions. The instructions typically say what the part builds, how to
build it, how to tear it down, and what it costs while it is running.

| Part | Builds |
| --- | --- |
| [00 aws-account](parts/00-aws-account/README.md) | An AWS account ready to build in |

## License

Licensed under either of

 * Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or <http://www.apache.org/licenses/LICENSE-2.0>)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or <http://opensource.org/licenses/MIT>)

at your option.

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall
be dual licensed as above, without any additional terms or conditions.
