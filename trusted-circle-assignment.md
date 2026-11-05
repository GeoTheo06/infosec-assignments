# The Trusted Circle

## Assignment: build a trusted network while another team tries to infiltrate it

Status: archived earlier draft. The balanced-role game in trusted-circle-game.md supersedes this document, including its scoring and winner rules. The earlier text below is retained for reference only.

## Student brief

Your team must establish a network in which authorized members can exchange confidential messages and issue authenticated commands. Another team can observe the public discovery channel, publish identities and keys, and submit malicious protocol messages. They want to become trusted members, read a protected message, or impersonate an authorized sender.

You win by maintaining useful communication while enforcing the membership policy. Rejecting every connection does not count as a secure working network.

## Learning objectives

- Distinguish an asserted name, proof of possession of a private key, and permission to join a group.
- Establish trust in a public key using an explicit initial trust anchor.
- Bind membership credentials and signatures to the intended key, group, round and operation.
- Protect message confidentiality and integrity, and prevent replay.
- Remove a compromised member and protect subsequent communication.
- Explain a security claim using a concrete message trace.

This applies the supplied course's public-key cryptography, access control, authentication protocols and key-management material. A short primer introduces the game's membership-credential format and approval protocol. It does not assume a prior IDOR or offensive network-tools lecture.

## Teams, roles and duration

Two teams of three students share an arena. One team defends and the other attacks. Each defender operates a distinct logical node with its own key pair. In a second session, roles reverse and both teams use fresh keys, identifiers and challenge values. The second defending team runs its own prepared implementation.

Suggested preparation: 3-5 hours per student using the provided scaffold. Suggested live play: two 90-minute sessions. These estimates require a novice pilot.

Use several independent arenas for a large class, with a projected class scoreboard. Every arena uses the same kinds of events and the same time/query budgets. Referee-controlled legitimate clients prevent a team's grade from depending entirely on another student group's implementation.

## What the teaching team provides

1. A relay and public discovery board. Display names, claimed sender fields and directory entries are untrusted; the relay does not authenticate a claim merely by delivering it.
2. A node scaffold with working transport, serialization, cryptographic helpers and command-line or browser controls. Students implement admission, verification and membership-state handling rather than a socket stack or cryptographic primitive.
3. A pinned course public key and round-specific admission credentials for the initial founders. Each student retains their own game private key.
4. A private referee service that creates authorized newcomer credentials, announces revocations, generates fresh challenges and observes outcomes.
5. A common vulnerable reference network for attacker practice, separate from the student competition.
6. A reset mechanism, structured traces and an automatic scoreboard.

The transport and scoreboard are course infrastructure. They are outside the attack surface. Application-level discovery, admission and message handling are inside it.

## The membership policy

Initially, the three defender nodes are authorized founders. Their admission credentials are signed by the course key and bind their identities to their public keys, arena, round and roles.

Later, the referee introduces legitimate newcomers whose keys were not available when the implementation was submitted. Each receives a signed admission credential. Attackers may hold valid course identities or credentials for other arenas, but do not receive admission permission for the target group.

For this exercise, a new member requires:

1. A valid course-signed admission credential for the current arena and round.
2. A fresh proof of possession of the private key bound to that credential.
3. Approvals from two distinct currently authorized founders, covering the same applicant key and membership request.

Students decide the exact message layout and state handling within the supplied interface. Approvals must not be transferable to a different applicant, key, group or request. Repeating one founder's approval does not create two approvals.

This rule makes trust bootstrapping explicit. A name, an uploaded public key or a confident introduction alone cannot establish that a stranger is authorized.

## Defender requirements

Build a protocol that allows the three founders to discover and authenticate one another, form the group, and exchange protected messages. Then support authorized joins, membership changes and revocation.

The network must:

- Admit valid newcomers within the published time limit.
- Keep unauthorized keys from gaining membership privileges.
- Keep protected plaintext out of the public channel.
- Authenticate the sender and bind each operation to its arena, round and intended recipients.
- Reject duplicate or stale protocol messages where they would repeat an operation.
- Process revocation and change future communication protection when a former member could retain an old group key.
- Continue accepting legitimate messages after a repair or membership change.

The crypto helpers may provide signatures, authenticated encryption, random challenges and key establishment. Successful encryption or signature verification alone is not a membership decision. Standard cryptographic libraries are allowed; custom primitive design is not required.

The instructor must define a canonical encoding or supply the serializer, so grading does not become an exercise in ambiguous JSON signing.

## Attacker objectives

Choose and combine attack ideas inside the arena. Examples include publishing an impostor key under an authorized name, replaying a captured join or approval message, substituting an applicant key, using a credential from another group, reusing one founder's endorsement, or exploiting inconsistent membership state between nodes.

After the compromise event, also test whether the network continues trusting a revoked identity or protecting new messages with an old key.

Three outcomes count as successful attacks:

| Objective | Required proof |
|---|---|
| Unauthorized membership | An attacker-controlled key obtains a membership-only operation or protected read. A displayed welcome message or open connection alone is insufficient. |
| Confidentiality breach | The attacker submits an exact fresh, unpredictable secret that was delivered only through the target network to its authorized recipients. |
| Sender impersonation | A node executes a fresh referee-selected protected command as an authorized identity, although that identity did not authorize it. |

For impersonation, simply replaying an operation already executed does not meet the objective unless the challenge specifically tests duplicate execution. Each objective has a separate challenge identifier and proof rule.

All attempts use course-issued identities, keys and synthetic data. Flooding, attacking the relay/grader, accessing devices or personal accounts, and obtaining other students' private files are outside the game. Public attempts share an equal rate limit. A team may not intentionally give its opponent secrets or arrange a staged compromise.

## The live session

| Time | Event | What it tests |
|---|---|---|
| 0-10 min | Connect, reset and verify the arena. | Operational readiness. |
| 10-25 min | Founders exchange credentials, form the group and deliver initial messages. | Trust establishment and basic functionality. |
| 25-40 min | Referee introduces previously unknown authorized members. Attackers can also request admission. | Enrollment, private-key possession and authorization. |
| 40-60 min | Open attack period with visible traces; defenders can patch. | Key substitution, replay, message integrity and state consistency. |
| 60-70 min | A designated ordinary member's game key is exposed; the referee publishes its revocation. | Recovery, exclusion and future-message protection. |
| 70-85 min | Freeze defender submissions and run the final challenge sequence. | The final network under fresh legitimate and adversarial inputs. |
| 85-90 min | Reveal outcomes and show one decisive trace per arena. | Shared learning and public result. |

The exposed member is not a founder in the first version of this exercise. That keeps founder-quorum recovery out of the core assignment.

A compromised member was authorized before revocation. Reading material that it legitimately obtained before that event does not count as an attack win. After a fixed grace period, newly generated protected messages and operations become the scored targets. Revocation cannot make someone forget old plaintext.

## Automatic scoring and winning

Publish the metric definitions and service threshold before play. Use only final-round events to decide the arena winner; earlier phases remain visible as learning/progress scores. Final-round secrets, request identifiers and commands are fresh.

### Defender score: 100 points

- **40 service points:** proportion of scheduled legitimate joins, deliveries and commands completed correctly within the time limits. The referee supplies enough workload to distinguish a usable network from a locked-down one.
- **20 admission points:** no unauthorized membership objective succeeds in the final round, and the fixed invalid-credential/revocation tests are rejected correctly. This category passes or fails.
- **20 confidentiality points:** no final-round protected secret is recovered by the attackers, and fixed plaintext-exposure tests pass. This category passes or fails.
- **20 authenticity/replay points:** no unauthorized final-round command succeeds and the fixed sender/replay tests pass. This category passes or fails.

An untested property is not automatically declared secure: fixed referee attack probes supplement the opposing team's attempts. The scoreboard labels the result as passing this challenge set, not as proof of universal security.

### Attacker score: 100 points

- **40 points:** confirmed unauthorized membership.
- **30 points:** confirmed recovery of a final-round protected secret.
- **30 points:** confirmed unauthorized command or the specified duplicate-execution objective.

Each category scores once. Sending the same successful request many times does not create more points.

### Arena result

- **Defenders win:** every scheduled authorized newcomer completes admission and at least one protected operation within its time limit, at least 80% of the scheduled legitimate service checks pass, all fixed security checks pass, and no attacker objective succeeds in the final round.
- **Attackers win:** at least one final-round attacker objective is confirmed.
- **Service failure / no winner:** no attacker objective is confirmed, but at least one defender winning condition fails.

The class scoreboard shows the arena result, legitimate-service percentage, each security category and verified attack objectives. Award a defending champion and an attacking champion separately, using equal challenge budgets. Keep the competition result separate from the academic grade.

## How the grader establishes the result

The referee maintains the ground-truth authorization roster and controls challenge creation. Defender submissions are frozen and executed in isolated course-hosted workers or containers for the final round. The platform uses a fixed interface for delivering inputs and observing outputs; student code cannot write scoreboard events directly.

Automatic checks include:

- A legitimate client decrypts a fresh message and returns the expected receipt.
- An authorized newcomer obtains the intended operation; a credential with the wrong group, key binding or validity does not.
- The same protected operation does not execute twice.
- New messages remain accessible to current members after a departure, and are unavailable to the revoked key in the tested scenario.
- An attacker provides the exact secret for its challenge, or the platform observes a protected command actually execute.

Screenshots, a self-reported accepted flag, or a message signed by a student key are not substitutes for the observed event. Audit logs record which input and state transition caused the outcome. The challenge receiver and command sink remain referee-controlled.

A representative final sequence contains a valid join, a valid message, a copied approval with a new applicant key, an old-round enrollment replay, duplicate endorsements, an out-of-arena credential, a revoked sender, a post-revocation secret, and another legitimate delivery. Randomize the order and values across equivalent arenas.

## Academic grading

Recommended split:

| Component | Weight | Assessment |
|---|---:|---|
| Defender implementation | 40% | Hidden reference tests of valid operation, admission, replay and revocation. |
| Attacker method | 30% | Submitted attack reproduced against fixed vulnerable reference instances; a real opponent compromise may demonstrate the same outcome. |
| Reproducibility | 10% | Clean reset and scripted reproduction of one experiment; no dependency on secret state from a past round. |
| Individual explanation | 20% | Each student explains a trace and predicts the result of a small fresh change. |

An attacker does not lose academic credit merely because their assigned opponent built a secure implementation. Every team has access to equivalent vulnerable reference instances and common grading objectives. A defender is not graded solely on how skilled the opposing attackers happen to be.

Submit the protocol/attack code or configuration, a compact message/state diagram, and a short explanation of one successful attack or rejected attempt. Describe the trust anchor, admission rule, freshness mechanism and revocation behavior. Include an AI/resource declaration if required by the course's approved policy; this assignment does not amend that policy.

## Example end-of-game reveal

The public board initially shows only submitted attempts, service levels and provisional outcomes, with secrets and exact exploit payloads withheld until the round closes.

At the reveal, the referee shows: an attacker copied a valid endorsement for Alice but replaced the applicant key with their own. One network counted the endorsement without checking the key binding and admitted the attacker. Another rejected the mismatch. The replayed request, the precise validation difference and the resulting protected operation make the winner visible to the whole class.

A second example can show a network that rejected all attacks but also refused every authorized newcomer. It failed the service condition, which illustrates the difference between useful access control and simply refusing to operate.

## Teaching and implementation notes

- Keep initial authorization explicit. Hidden attacker identities do not eliminate the need for an authenticated source of permission for legitimate newcomers.
- Keep membership identity separate from the relay's account identity and from an unverified display name.
- Let students see the rules and wire format; security should not depend on hiding the protocol from attackers.
- Restrict the first version to a trusted course issuer and an uncompromised founder quorum. Malicious founders, partition recovery and decentralized consensus are advanced extensions.
- Do not include arbitrary packet dropping or flooding in a round whose service grade assumes messages can be delivered. Protocol-level corruption/replay can be tested with controlled budgets and a reliable underlying transport.
- A browser interface can operate hosted nodes; a Python client can expose the same actions. The exercise does not require wireless adapters, Wi-Fi password cracking or a VPN implementation.
- For a lower-code version, retain the same game and scoring but supply selectable verification rules and message-building tools. For a programming assignment, expose the admission and message-processing hooks.
- Test the reference client, hidden cases, reset and score instrumentation before piloting with students. A secure solution should be achievable within the scaffold, and a failing implementation should produce explainable traces.

Useful primary implementation references:

- [GNU Privacy Handbook: key exchange and fingerprint verification](https://www.gnupg.org/gph/en/manual.html) - the identity/key-binding problem and an authenticated verification channel. Its historical algorithm/key-size examples should not be copied as current defaults.
- [RFC 8032: EdDSA](https://www.rfc-editor.org/rfc/rfc8032.html) - a standard signature primitive if the supplied helpers use Ed25519.
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446.html) - authenticated secure transport for the course control plane. The application-level membership protocol remains the students' task.
