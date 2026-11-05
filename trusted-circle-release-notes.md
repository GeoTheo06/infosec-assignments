# Trusted Circle — instructor release decisions

Draft, 6 November 2026.

The [student handout](trusted-circle-student-handout.md) translates the [balanced-role specification](trusted-circle-game.md) into student instructions. It preserves the five challenges, membership policy, two sessions and scoring while making the following points explicit:

- All three defending students begin as course-authorized founders; two approvals are required only for subsequent newcomers.
- Referee clients provide unknown legitimate newcomers, so a group is not limited to its three human founders.
- Students edit trust and membership hooks in a supplied application; the course hosts the relay, referee and isolated final execution.
- Reference targets, the editable live network and the frozen final submission have separate purposes and evidence.
- The scheduled compromise affects an ordinary admitted member, and revocation tests use fresh post-deadline information.
- Students must demonstrate both rejection of attacks and continued legitimate operation.

## Decisions required before publishing

1. **Teaching format:** confirm the programming version assumed by the handout, or select the lower-code variant described in the specification. Publish the exact work students own.
2. **Student interface:** choose the browser/Python workflow and implement a runnable starter. Supply exact file names, hooks, commands and message contracts; the current documents cannot provide these yet.
3. **Challenge behavior:** choose each concrete vulnerable path and protected operation. In particular, define the replay scenario and how the application interface exposes key substitution for the MITM challenge. Access to a shared relay alone is not sufficient.
4. **Event orchestration:** implement initial founder credentials, fresh newcomer clients, ordinary-member compromise, authenticated revocation and resets that restore the required event history.
5. **Scope and workload:** pilot both roles with novice and experienced participants before confirming five challenges, 3–5 preparation hours and two 90-minute sessions.
6. **Limits and fairness:** confirm timeouts, total request allowances, reference availability until the common deadline, final attack budgets and infrastructure failure handling.
7. **Assessment and logistics:** confirm grading weights, individual checks, report limits, dates, submission/support routes and the existing course AI policy.

The architecture, automation and pilot remain outstanding. The handout is a reviewable draft, not a claim that the platform is ready. Any subsequent change to the game rules should be reflected in both the specification and student handout.
