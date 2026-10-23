# Local output capture

Captured on 23 October 2026 from base revision `407261b7b63a0a3623bae54ca11278b277bd7338` with the documentation and demo additions in this commit.

The v4 release archive was downloaded and its SHA-256 matched the root README. Its included verifier passed 2651 manifest file checks, selection reconstruction, two source-ordered sample checks and 18 direct-fault comparisons. This verifies saved material, not the validity of the research claim, acceptance by a venue, model outputs or newly rerun product tests. output.json is the actual verifier stdout. The PNG is a rendered transcript.

Commands from a fresh scratch directory:

```sh
gh release download saner-2027-evaluation-2026-10-19 --repo olegpustovit/agent-test-pruning --pattern review-supplement-v4.tar.gz
sha256sum review-supplement-v4.tar.gz
tar -xzf review-supplement-v4.tar.gz
cd artifact-supplement-v4
uv run verify_public_evidence.py
```

Image: [verification.png](verification.png)
