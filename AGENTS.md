# Installing the NMR review skills

When asked to install `reaction-nmr-review` from this repository, install its required companion `ailsa-nmr` in the same operation. The two skills are independent folders under `skills/`. Copying only the main folder leaves the installation incomplete.

1. Resolve one skills directory that the receiving host discovers. From this checkout, run `bash scripts/install-skills.sh` or pass the verified directory explicitly. Use the bundled installer even if the user mentioned only the main skill.
2. Verify that both destination folders contain their own `SKILL.md` and supporting files. The script checks both against the bundle. Keep divergent existing copies intact and report any conflict.
3. Verify the local NMR environment separately using [the runtime setup guide](docs/ailsa-runtime.md). Reuse a working installation when available. For a full setup on a fresh host, follow that guide within the user's requested scope. Record missing prerequisites, unavailable downloads, or any capability you could not verify. A missing statistics schema is compatible with restricted CASE when the spectra and formula support it.
4. Report both installed skill paths and the verified runtime capabilities separately. If the host exposes a skill inventory, confirm both entries. If a session refresh is needed, tell the user how to check the inventory in a new session.

Use [README.md](README.md) for the user-facing install and invocation instructions.
