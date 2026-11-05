# The Trusted Circle

## A cooperative security game with attackers, defenders and a live scoreboard

Balanced-role edition | 15 October 2026

This is the complete proposed game and assignment specification. The course arena, client scaffold and automatic grader described here still need implementation and a small pilot. It supersedes the earlier trusted-circle-assignment.md draft.

## 1. The game in one paragraph

Three students must establish a trusted network, communicate securely, admit legitimate newcomers and remove compromised members. Three other students try to exploit mistakes in that process. Both sides can earn points in the same challenge: attackers demonstrate a weakness in an immutable vulnerable starting instance, while defenders secure their live network and pass independent tests. Attacking the opponent's hardened network earns a small competition bonus. The teams then exchange roles. At the end, the class sees the best attacking team, the best defending team and the best overall team, together with the message traces that explain the results.

## 2. What students should learn

- An asserted name is different from a verified identity and from permission to join a group.
- Possessing a private key proves control of that key; it does not automatically establish what its holder is allowed to do.
- Public keys need an authenticated binding to the identities or roles they represent.
- An encrypted exchange still needs peer authentication, correct recipient selection and integrity protection.
- Membership approvals and signed messages need the right identity, key, group, round and operation bindings.
- Freshness and replay prevention require protocol state, not just a signature.
- Revoking a member must affect subsequent access and, where necessary, subsequent encryption keys.
- A secure network must remain usable by legitimate participants.

These objectives connect to the course's public-key cryptography, hashing/MACs, access-control principles, authentication protocols and key-management material. The game-specific credential format and interfaces require a short preparatory explanation. No prior IDOR lecture, wireless attack experience or cryptographic primitive implementation is assumed.

## 3. Teams and arenas

### Team size and roles

Use teams of three. Pair two teams in each arena:

- **Session 1:** Team A defends; Team B attacks.
- **Session 2:** Team B defends its own implementation; Team A attacks.

Each defender controls one logical node with its own key pair. Each team prepares both a defensive implementation and attack methods. Rotate responsibilities within teams so every student helps operate a node, inspect a trace and develop an attack or fix.

The second session uses fresh identities, keys, credentials, secrets and request identifiers. The second defender does not inherit the first defender's code or a compromised network state.

### What “network” means

This is a logical peer group running over a course-hosted relay. Students may use a browser interface or a Python client. Wi-Fi or Ethernet provides ordinary connectivity; special wireless adapters, radio injection and VPN implementation are not required.

The public discovery board and application messages are visible to the assigned attackers. Joining the trusted group means obtaining a protected group privilege, not simply connecting to the relay or opening a socket.

### Suggested duration

- Preparation: 3-5 hours per student using the supplied scaffold, subject to pilot results.
- Live game: two 90-minute sessions, with roles reversed in the second.
- Submission: code/configuration, attack reproduction and a concise explanation after the second session.

For a large class, run multiple independent arenas with identical challenge types and budgets. Referee clients provide legitimate traffic so a team's assessment does not depend entirely on another student group's implementation or attendance.

## 4. What the teaching team supplies

1. **A working node scaffold.** Transport, canonical message encoding, cryptographic helpers, basic controls and structured tracing are provided. Students implement the trust and membership logic through documented hooks.
2. **A public discovery channel.** Students can publish names, public keys, introductions and membership requests. These claims are untrusted until the application validates them.
3. **An initial trust anchor.** Every node starts with the authentic course public key. The course issuer signs admission credentials; its private key remains with the referee.
4. **A live network instance.** Defenders modify and operate this instance collaboratively.
5. **An immutable starting snapshot.** The platform preserves the instructor's vulnerable starting version before defenders change it. Attackers retain access to suitable vulnerable targets even when defenders repair the live network quickly.
6. **Five isolated attack reference instances.** Each exposes one intended weakness for one challenge, using equivalent per-team randomized values. They prevent one broad compromise from automatically satisfying every challenge.
7. **Referee-controlled clients and sinks.** These issue legitimate requests, receive protected messages and record whether a command actually executes.
8. **Automatic grading, resets and a scoreboard.** Student code cannot award itself points or modify referee logs.

The source/interface and security requirements are available to both sides. Security must not depend on keeping the protocol design secret. Private keys and fresh referee secrets remain private except during the specified compromise event.

## 5. Trust and membership rules

### Founders

The three defending nodes are the initial founders. Their course-signed credentials bind:

- The arena and round.
- An identity and public-key fingerprint.
- The founder role and permitted operations.
- A validity period or equivalent round validity.

Founders must discover and authenticate one another before using the trusted group. A directory entry or claimed sender name alone is insufficient.

### New members

During play, the referee introduces previously unknown legitimate newcomers. Their public keys are not available when the defender implementation is submitted. Some may be operated by other students; reference clients ensure an equivalent assessed workload in every arena.

A newcomer must have:

1. A valid course-signed admission credential for the current arena and round.
2. A fresh proof of possession of the private key bound to that credential.
3. Approvals from two distinct currently authorized founders, covering the same applicant key and membership request.

Approvals must not be reusable for another applicant, another key, another group or an unrelated request. Two copies of one founder's approval do not count as two founders.

Attackers may possess valid general course identities or credentials for other arenas. They do not receive permission to join the target group. Authentic identity and target-group authorization must be evaluated separately.

### Membership changes

The referee publishes authenticated membership events, including revocation. The first version of the game compromises an ordinary member, not a founder, so recovery of a malicious founder quorum remains outside the core assignment.

A revoked participant may retain old private keys, old group keys and old plaintext. The requirement is to protect newly generated messages and operations after the published grace period. Revocation cannot make a person forget information they previously received legitimately.

## 6. The five challenges

Each challenge offers **20 attacker points and 20 defender points**. Both sides can earn all 20 points on the same challenge, because the attack and the defensive repair are assessed against the appropriate versions of the network.

### Challenge 1: False identity

**Attack objective:** obtain a protected group privilege using an attacker-controlled key presented under an authorized identity.

The vulnerable reference instance contains an enrollment identity/key-binding mistake. The attacker may publish a misleading directory entry, substitute an applicant key, or misuse a credential/approval that belongs to another key.

**Defence objective:** authenticate the credential, check its identity/key/group binding, verify private-key possession, and admit the genuine newcomer.

**Machine evidence:** the attacker-controlled key completes a protected operation, or the repaired node rejects it while the legitimate applicant completes that operation. A welcome message, accepted transport connection or unverified membership display does not count.

### Challenge 2: Replay

**Attack objective:** reuse a previously valid request or approval to cause a prohibited second effect or an invalid new admission.

The reference instance provides a legitimate captured exchange and a state in which reusing it can cause the specified invalid effect. The challenge states whether the target is duplicate command execution, stale admission, or replay across rounds.

**Defence objective:** reject the replay while accepting the corresponding fresh, legitimate request. Bind freshness to the correct sender, recipient, operation and round.

**Machine evidence:** a referee operation counter or membership event shows the prohibited effect. Replaying an idempotent read and receiving the same harmless response does not count as a breach.

### Challenge 3: Man in the middle

**Attack objective:** substitute a key during the reference key-establishment exchange and recover a fresh protected message intended for the legitimate peers.

This reference instance isolates a peer-authentication or transcript-binding mistake. The intended vulnerability is not breaking a correctly chosen cryptographic primitive.

**Defence objective:** establish a channel with the intended authenticated peer, detect a substituted key, and still deliver a genuine protected message successfully.

**Machine evidence:** the attacker submits the exact unpredictable challenge plaintext; the repaired network rejects the substituted exchange and a reference peer successfully decrypts the legitimate message.

### Challenge 4: Message forgery

**Attack objective:** cause execution of a fresh protected command that the claimed authorized sender did not authorize.

The reference instance contains a sender-verification or signed-field-binding mistake. The attacker may alter a relevant command field, change its claimed sender or exploit an incomplete authenticated message.

**Defence objective:** authenticate the complete relevant command context and sender, reject altered or unauthorized messages, and execute a genuine command once.

**Machine evidence:** a referee-controlled command sink records the exact forbidden action and challenge identifier. This is distinct from Challenge 2's reuse of an already valid operation.

### Challenge 5: Revocation

**Attack objective:** after the removal deadline, use a former member's retained state to access a newly generated secret or perform a now-forbidden protected operation.

The referee supplies the removed ordinary member's permitted retained game state. The reference instance has a stale-membership or future-key-update weakness.

**Defence objective:** exclude the removed identity, update future communication protection as needed, and keep current members communicating.

**Machine evidence:** the old key/state can or cannot recover a fresh post-deadline secret or complete the protected operation, while a current member's corresponding operation succeeds.

Information obtained legitimately before revocation does not count toward this objective. Every assessed secret is generated after the grace period.

## 7. How both roles have an achievable goal

The platform separates three targets:

| Target | Purpose | Can defenders change it? |
|---|---|---|
| Immutable starting snapshot / challenge references | Demonstrate and reproduce the five attack methods. | No. |
| Live student network | Collaborate, harden the protocol, observe attacks and recover. | Yes, until the final freeze. |
| Frozen final submission with fresh referee tests | Assess whether the defensive requirements are met. | No, during final assessment. |

An attacker therefore does not lose the opportunity to score because an opponent fixes a bug early. A defender does not lose all credit because an initial version was compromised: a correct repair can earn full defence points.

For example, the attackers exploit enrollment-key substitution in the reference instance and earn the attack points. The defenders bind the approval to the actual applicant key and pass the final admission tests, earning the defence points. Both sides achieved the intended learning outcome.

This creates comparable opportunities, not a promised 50/50 probability of breaking a hardened network. Difficulty, time limits and reference weaknesses must be calibrated with a pilot. A correctly implemented final network may resist every live attack.

## 8. Live session schedule

| Time | Event | Roles and scoring |
|---|---|---|
| 0-10 min | Reset, connect and verify the arena. | Confirm reference and live instances are separate; establish equal budgets. |
| 10-25 min | Founders form their network. | Defenders authenticate one another and communicate; attackers inspect the public interface and begin reference challenges. |
| 25-40 min | Newcomers arrive. | Legitimate clients and attackers request admission; defenders must keep the network usable. |
| 40-60 min | Open attack and repair period. | Attackers pursue reference objectives and live attacks; defenders inspect traces and patch. |
| 60-70 min | Compromise and revocation event. | Referee exposes an ordinary member's retained game state and publishes revocation. |
| 70-85 min | Final freeze and live test window. | Freeze defender code, use a clean final reset, run fresh legitimate/security tests and the bounded live competition challenge. |
| 85-90 min | Reveal. | Show verified outcomes, current scores and one short explanatory trace per arena. |

Reference attack work remains available until the common submission deadline, so a live-session equipment interruption does not remove the core attack opportunity.

The second session repeats the schedule with roles reversed and fresh equivalent instances. Do not reuse a session-one flag or key as a session-two target.

### Compromise timing

Default revocation grace period: 60 seconds after the authenticated notice reaches the nodes. The instructor may change this after piloting, but must publish one value for all arenas.

The final round starts after the grace period and uses entirely new secrets and operation identifiers. The final reset must reproduce the applicable revocation event; it must not accidentally restore the revoked member's access.

## 9. Core automatic scoring

### Attack score A: up to 100

Each of the five challenges has 20 points:

- **12 points:** achieve the specified prohibited effect against its vulnerable reference instance, verified by the referee.
- **8 points:** reproduce the method against a fresh equivalent reference instance with new identities, keys or challenge values, using the submitted attack script or supported replay procedure.

The reproduction must adapt to the new instance. Submitting an old flag, copying an old encrypted artifact or replaying a response from another team earns no reproduction points.

A category can score once. Repeating one exploit many times does not produce more points. A success in one reference instance is not automatically counted in another challenge; each has its own scope, proof condition and fresh target.

### Defence score D: up to 100

Each of the five challenges has 20 points:

- **10 functionality points:** its legitimate joins, messages or commands succeed in the final tests.
- **10 protection points:** its malicious test cases are rejected correctly, with the corresponding legitimate operation still working.

Protection points are gated by functionality. The implementation cannot earn those points by rejecting every request or stopping the node. If partial credit is offered, the grader awards protection credit only for test pairs whose positive control also passed.

Every defender faces the same kinds of fixed referee attacks plus fresh equivalent hidden cases. An unskilled or inactive opposing team does not automatically produce full defence marks.

### Equal role weighting

After both sessions, every team has an attack score A out of 100 and a defence score D out of 100. The core game total is:

**Core total = A + D, maximum 200.**

Both roles contribute equally. It is possible for both opposing teams to earn full core credit by demonstrating successful attacks against vulnerable instances and successful defences in their own final networks.

## 10. The live competition and winners

Live bonuses create an extra contest against the opponent's hardened network. They do not change the academic grade.

### Live attack bonus: up to 10

During the final live window of its attacking session, a team earns 10 points for at least one verified protected-boundary breach against the opponent's hardened network. Additional repetitions or additional breaches do not increase this bonus.

A breach must satisfy one published objective and use a fresh final-window challenge. Success against a reference instance, a pre-freeze version or a prior round does not qualify.

### Live defence bonus: up to 10

During its defending session, a team earns 10 points if:

- No final-window live attacker objective succeeds.
- Every scheduled authorized newcomer completes admission and at least one protected operation within the required time.
- At least 80% of the scheduled legitimate service checks succeed.
- The fixed final security tests all pass.

The last two conditions stop a team from winning merely because the opponent made no effective attempt. The newcomer condition stops a team from keeping only its original hard-coded peers.

### Competition total

**Competition total = A + D + live attack bonus + live defence bonus, maximum 220.**

The bonuses are intentionally small. A strong opponent can affect at most the relevant live bonus, rather than eliminating the other team's main opportunity to succeed. The competition rewards tested attack and defence competence as well as live play.

### Awards

- **Best attacking team:** highest A plus live attack bonus, maximum 110.
- **Best defending team:** highest D plus live defence bonus, maximum 110.
- **Best overall team:** highest competition total, maximum 220.

Equal totals receive a shared placing. Do not break ties using raw request volume, computer speed or unannounced rules.

### What happens to a team that was breached?

An early breach does not eliminate anyone. Defenders may repair before the freeze and still earn their full core defence score. A verified final-window breach affects the live defence bonus and may expose a failing final test; it does not erase unrelated challenge points.

There is no “one breach means the attackers win the whole assignment” rule.

## 11. Automatic proof and referee design

The referee maintains the ground-truth roster: which identity/key is authorized for which group, role and time period. The referee's private issuer key, roster and secret generation are outside student control.

The grader observes real outcomes through a fixed interface:

| Property | Observable check |
|---|---|
| Authorized membership | A fresh authorized client completes a protected operation using its bound key. |
| Unauthorized membership | An attacker-controlled key gains a membership-only operation it was not granted. |
| Confidentiality | An attacker submits the exact unpredictable secret for a challenge and instance. |
| Legitimate delivery | The intended reference recipient decrypts the message and returns the expected challenge receipt. |
| Command authenticity | The referee command sink executes the exact challenge operation under the claimed authorization. |
| Replay prevention | The operation counter shows whether the same logical action executed again or a stale request gained a new privilege. |
| Revocation | Fresh post-deadline access fails for the removed member but succeeds for a current member. |

Student code runs in isolated course-hosted workers or containers for final assessment. It can emit application outputs through the fixed interface, but cannot write scoreboard events, access referee secrets directly or call a private scoring endpoint.

The receiver and protected command sink remain referee-controlled. Screenshots, self-reported success strings and an acknowledgement generated by the attacker are not proof of a protected action.

Each result records an arena ID, round ID, challenge ID, target version and reproducible trace. Private audit metadata records the submitting team even when the application message contains a spoofed identity.

Randomize values and case order across equivalent instances. Keep the same intended difficulty and budgets. Resets clear membership/replay state unless the test specifically requires prior state; revocation tests explicitly recreate their event history.

### Default operational limits for piloting

- Newcomer admission: 120 seconds after a complete legitimate request is delivered.
- Legitimate message or command: 10 seconds after delivery to a running node.
- Revocation grace period: 60 seconds after notice delivery.
- Attack API budget: start with a per-team limit of 5 requests/second and a published total allowance per challenge; adjust after measuring the intended attacks.

Freeze the final values after the pilot and publish them before students begin. Measure server-side event times to reduce differences caused by student devices. Instructor infrastructure failures pause or invalidate affected tests; they do not count as a security win.

## 12. Rules of play

### Allowed

- Observe the assigned arena's public application channel and discovery board.
- Generate game key pairs and publish false claimed identities inside that arena.
- Submit, replay, reorder or modify application messages through the supported attack interfaces.
- Analyze the supplied protocol and source, and use the supplied cryptographic helpers or permitted standard libraries.
- Develop attack scripts and inspect the traces available to the team.
- Contact other participants through the game's public interaction mechanisms using fictional game identities.

### Outside the game

- Attacking the relay, scoreboard, course accounts, host operating systems or unrelated services.
- Flooding, radio disruption or arbitrary packet dropping that prevents the assumed reliable transport from operating.
- Accessing another student's private files or personal accounts.
- Obtaining private keys except through an allowed protocol flaw or the referee's explicit compromise event.
- Intentionally giving an opponent a secret, disabling protection to arrange a win, or sharing private solution artifacts across teams contrary to course rules.

The public attack budget applies equally to all teams. Payloads use synthetic course data. Founder compromise, issuer compromise, malicious quorum members and distributed-consensus recovery are advanced extensions outside the first version.

## 13. Academic grading

Competition results and academic assessment are separate. The live bonuses are for the leaderboard only.

| Component | Weight | How it is assessed |
|---|---:|---|
| Attack methods | 40% | A out of 100: five reference objectives and reproduction on fresh instances. |
| Defensive implementation | 40% | D out of 100: legitimate operation and security tests for all five challenges. |
| Individual understanding | 20% | Each student explains a trace, states the trust assumption, and predicts a fresh small change. |

**Academic mark out of 100 = 0.40 A + 0.40 D + 0.20 I**, where I is the individual explanation score out of 100.

Thus, 80% can be checked automatically and 20% is assessed individually. Team members share A and D but receive their own I scores. Use an accessible equivalent check if an oral/practical format is unsuitable for a student.

An attacker is not penalized academically for drawing an opponent with a secure live network. A defender must pass reference tests even if its live opponents are unsuccessful. Machine speed, number of requests and polished writing are not separate performance criteria.

### Submission

One team submission contains:

1. The defensive code/configuration and a clean reset/run procedure.
2. Attack scripts or supported reproduction procedures, indexed by challenge.
3. A compact protocol/state diagram covering trust establishment, admission and revocation.
4. An evidence manifest linking each claimed result to its arena, challenge, version and trace.
5. A concise explanation of one attack and its corresponding repair, including one remaining limitation.
6. An individual contribution record and any resource/AI-use declaration required by the approved course policy.

Private game keys are not part of the report. A reproducible course key-generation/reset procedure is sufficient. A stored success flag alone is not a method.

## 14. AI assistance and individual understanding

Use the course's published AI policy. If the professor permits disclosed AI assistance, students may use it for setup, debugging and code suggestions, but remain responsible for running the work and explaining every claim. This game specification does not amend the supplied course's existing restriction on generated submitted answers.

The practical requirement is that students operate their nodes, inspect the evidence and handle new values or state. Individual checks can ask:

- Which key was trusted here, and why?
- What changes if the applicant key changes but the name remains the same?
- Why did the replay succeed in the starting instance?
- What state must change after revocation?
- Can the network reject this attack and still admit this legitimate newcomer?

The examiner changes one small input and asks for a prediction before executing it. Do not infer understanding or misconduct from writing style or an AI-detector score.

## 15. The live scoreboard and final reveal

### Suggested scoreboard columns

| Team | Attack /100 | Defence /100 | Live attack /10 | Live defence /10 | Total /220 |
|---|---:|---:|---:|---:|---:|
| Example team | 80 | 90 | 10 | 0 | 180 |

During play, show verified category progress, legitimate service levels and provisional totals. Clearly label reference successes and live successes; they must not appear interchangeable. Defence results remain provisional until the frozen hidden tests finish.

Withhold secret values and exact successful attack payloads until the relevant round closes. The final board shows the three awards and shared placings if needed. Publish the machine-verifiable scoring breakdown and provide a route for reporting grader/infrastructure errors.

### Example reveal

1. The attacker copied an approval for Alice and replaced Alice's applicant key with their own.
2. The vulnerable reference instance checked the approving founder but failed to check which applicant key was approved. A protected operation succeeded.
3. The same method reproduced against a fresh reference instance: the attackers earned all 20 points for Challenge 1.
4. The defenders bound approvals to the applicant key and request, verified key possession, and passed the final legitimate and malicious tests: they earned all 20 defence points for Challenge 1.
5. A later attempt against the hardened live network failed. If the defender also met the other final conditions, it retained its live defence bonus.

Both sides achieved their core goal. The class sees what failed, what repaired it, and which version of the system each result describes.

A second reveal can show a network that rejected all malicious requests but also excluded legitimate newcomers. Its functionality tests failed, so it could not obtain full defence points or a live defence bonus.

## 16. Instructor preparation checklist

### Implement before release

- A canonical message serializer and documented student hooks.
- The course issuer, signed admission credentials and authenticated revocation notices.
- Working founder/newcomer reference clients and safe key generation.
- The live relay/discovery board, preserving untrusted application identities while keeping authenticated audit attribution private.
- The instructor's immutable starting snapshot and five scoped vulnerable reference targets.
- Isolated final workers, protected receivers/command sinks and fresh challenge generation.
- Automated positive/negative test pairs, reset logic and attack reproduction.
- Rate limits, instance ownership, scoreboard separation and evidence export.

### Pilot for balance

Have at least one novice and one experienced pilot team try each role. Measure setup time, time to a first attack success, time to a correct repair, reproducibility, service failures and the number of challenges completed.

Adjust the scaffold, hints, test budgets or intended vulnerability complexity if one role consistently completes much more work in the available time. Give both sides staged hints on an equivalent published schedule. Do not create balance by requiring an otherwise correct final network to remain vulnerable.

The desired outcome is that students can complete substantial core work in both roles and that full success is attainable with sound reasoning. A 50/50 live breach rate is not itself the educational objective.

### Keep scope manageable

The first implementation assumes a trusted course issuer, reliable underlying transport and an uncompromised founder quorum. Use standard signature/authenticated-encryption/key-establishment helpers. Avoid requiring students to implement primitives, distributed consensus, wireless drivers or a production-grade messaging system.

For a lower-code offering, provide selectable validation rules and message-building tools through the same interface. The scoring and trust requirements remain the same. For the programming version, students fill the verification and membership-state hooks.

## 17. Relationship to the supplied course

| Material | Connection |
|---|---|
| 03-Crypto 2.pdf | Public-key cryptography and key establishment. |
| 04-hashing.pdf | Integrity, MACs and hashing. |
| 05-AccessControl.pdf | Authentication versus authorization, complete mediation, roles/attributes and enforcement. |
| 06-Protocols.pdf | Replay, challenges, identity binding and mutual authentication. |
| 08-GPG.pdf | Public-key authenticity, fingerprint verification, signatures and revocation.
Useful primary references for the teaching team:

- [GNU Privacy Handbook](https://www.gnupg.org/gph/en/manual.html): key exchange, fingerprint verification and identity/key binding. Its historical algorithm/key-size defaults should not be copied as current implementation choices.
- [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html): EdDSA signatures if the supplied helpers use Ed25519.
- [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html): TLS 1.3 for the trusted course control plane. Application-level membership decisions remain the students' task.

## 18. Student-facing summary

Build a working trusted group with your teammates. Admit the right newcomers, keep messages confidential, authenticate commands and remove compromised members. In the other role, expose the five kinds of weaknesses in vulnerable reference networks and try your methods against an opponent's hardened network.

Each challenge offers 20 points for demonstrating the attack and 20 points for securing the network. Both sides can succeed. You will play both roles, and the class will see the strongest attackers, the strongest defenders and the strongest overall team.
