# The Trusted Circle: student assignment

This handout describes the proposed programming assignment. The arena, starter code and grader are not yet implemented. The teaching team must supply the release details listed at the end before assigning this work. The current rules come from [the game specification](trusted-circle-game.md).

## Your mission

Build a private group that admits authorized people, exchanges protected messages and commands, and removes a compromised member. Then take the attacker role and demonstrate how mistakes in those rules can be exploited.

You work in a team of three. Your team plays both roles against another team of three, in two 90-minute sessions. Both teams can earn full academic credit: attacks are assessed against deliberately vulnerable reference targets, and defence is assessed against fresh tests of your implementation.

You should finish able to explain who a key belongs to, why its holder is authorized, what a signature actually protects, how you prevent replay, and what must change when someone loses access.

## What runs where

An **arena** is your pair of teams' isolated game environment on course infrastructure. A **node** is one running participant in your group. Each defending student operates a founder node with its own key pair.

| Component | What you use it for | Who controls it? |
|---|---|---|
| Browser or Python client | Operate your node, submit requests and inspect traces | You, through the supplied interface |
| Node starter application | Implement credential checks, membership decisions, message verification and revocation handling | Your defending team edits the documented student hooks |
| Public discovery board | Publish claimed names, public keys and join requests | Course service; the posted claims are untrusted |
| Message relay | Carry application traffic between participants | Course service |
| Course issuer | Sign credentials that bind identities and keys to permitted roles, arenas and rounds | Teaching team; its signing key remains private |
| Referee and legitimate clients | Introduce authorized newcomers, generate challenges, revoke a member and observe real outcomes | Teaching team |
| Five vulnerable reference targets | Demonstrate and reproduce the five attacks | Teaching team; you cannot patch these targets |
| Grader and scoreboard | Test your work and display verified results | Teaching team |

The starter supplies transport, a consistent message encoding, cryptographic helpers and structured traces. Your task is to implement the security decisions through the supplied interface. You do not have to implement cryptographic algorithms or set up wireless interception. Final submissions run in isolated course-hosted workers or containers.

The assigned attackers can inspect the public discovery board and available application traffic, and submit messages through supported interfaces. A relay connection or a displayed name does not grant group membership.

## Before the first session

1. Form a team of three and read the supplied interface guide and credential-format primer.
2. Run the starter using the released setup instructions and confirm that you can inspect a message trace.
3. Prepare your defensive implementation and attack methods. Plan for approximately 3–5 hours of preparation per student; this estimate is subject to the pilot.
4. Rotate responsibilities so everyone operates a node, investigates a trace and contributes an attack or repair.
5. Check the published session dates, submission deadline and request limits.

## How membership works

### Starting the group

**All three defending students start as authorized founders.** The course issuer provides founder credentials for the current arena and round. Each credential binds an identity to a public key, role and permissions, with a validity period or equivalent round validity.

Every node begins with the authentic course public key, which lets it verify course-issued credentials. Your nodes must authenticate one another before trusting the group. The two-founder approval rule below applies to later newcomers; it is not how the initial three founders are appointed.

### Admitting a newcomer

The referee introduces authorized newcomers whose keys you do not know in advance. These may be automated reference clients or other student-operated clients. The group can therefore contain more than the three human founders.

Admit a newcomer only when all three conditions hold:

1. Their course-signed credential is valid and authorizes admission to this arena and round.
2. They provide fresh proof that they control the private key bound to that credential.
3. Two distinct, currently authorized founders approve the same applicant key and membership request.

An approval must not transfer to a different applicant, key, group, round or unrelated request. Two copies of one founder's approval count as one approval. A valid general course identity or a credential for another arena does not authorize admission here.

For example, Dana can join without being known beforehand because your code verifies the course's authorization, Dana's key ownership and the required founder approvals. Someone copying Dana's name or credential still has to satisfy every check. Hard-coding the original three keys and rejecting all newcomers fails the functionality tests.

### Removing a member

During the scheduled compromise event, the referee exposes an ordinary member's permitted retained game state to the attackers and issues an authenticated revocation notice. The member is not a founder.

After the published grace period, that member must lose protected access. Update membership checks and future encryption protection as needed, while keeping current members working. The removed member may retain old private keys, group keys and plaintext. The tests concern newly generated secrets and operations after the deadline, not information already received legitimately.

The proposed grace period is **60 seconds after notice delivery**; the final release must confirm it.

## Your five challenges

| Challenge | As an attacker | As a defender | Evidence the referee checks |
|---|---|---|---|
| 1. False identity | Use your key under an authorized identity to obtain a protected privilege | Validate the credential, key binding, key ownership and admission approvals; admit the genuine newcomer | Whether the relevant key completes an actual protected operation |
| 2. Replay | Reuse a valid captured request or approval to cause a prohibited second effect or invalid admission | Track freshness and context; reject the replay while accepting a fresh valid request | An operation counter or membership event showing the specified effect |
| 3. Man in the middle | Substitute a key during the vulnerable exchange and recover a fresh secret | Authenticate the intended peer and key exchange; still deliver legitimate protected messages | Exact recovery of the challenge secret, or successful legitimate delivery with substitution rejected |
| 4. Message forgery | Cause a fresh command to execute without the claimed sender's authorization | Authenticate the sender and all relevant command fields and context | The exact command executed at the referee-controlled receiver |
| 5. Revocation | Use the removed member's retained state to access a new secret or forbidden operation after the deadline | Exclude the removed member and protect future communication while preserving current members' access | Fresh post-deadline access attempts paired with a current member's successful operation |

Replay concerns reusing an already valid operation. Forgery concerns a fresh operation the claimed sender did not authorize. A harmless repeated read does not establish a replay breach.

For the man-in-the-middle challenge, the reference interface provides an opportunity to substitute key-establishment messages. Two people being online does not authenticate the keys their software accepts. An attack on the live network succeeds only if its implementation has a relevant weakness.

## Know which target you are using

| Target | Purpose | Can defenders edit it? |
|---|---|---|
| Preserved vulnerable starting version and five isolated reference targets | Demonstrate attacks, with a separate intended weakness and proof condition for each challenge | No |
| Opponent's live student network | Try attacks while defenders investigate and repair | Yes, until the freeze |
| Frozen final implementation | Assess defence with fresh legitimate and malicious tests, plus the live competition window | No during assessment |

A reference success and a live-network success are different results. Include the target version in your evidence. Breaking one reference does not automatically solve the other challenges. A correctly secured live network may resist all attacks.

## What happens during each session

| Time | Defending team | Attacking team / referee |
|---|---|---|
| 0–10 minutes | Reset and check your nodes and arena | Check reference/live target access and equal budgets |
| 10–25 minutes | Authenticate the three founders and exchange protected messages | Inspect the public interface and begin reference challenges |
| 25–40 minutes | Admit valid newcomers and reject invalid requests | Referee introduces newcomers; attackers try admission attacks |
| 40–60 minutes | Inspect traces, repair your implementation and keep service working | Continue reference attacks and attacks on the live network |
| 60–70 minutes | Process the authenticated revocation notice and remove the compromised ordinary member | Referee provides retained state; attackers test post-deadline access |
| 70–85 minutes | Freeze your code; the platform resets and assesses the final version | Fresh referee tests and the bounded final live attack window |
| 85–90 minutes | Review verified outcomes and explanatory traces | Scoreboard reveal |

The final reset recreates the required revocation history. It does not restore the removed member's access. Final challenges use fresh secrets and operation identifiers after the grace period.

In session two, swap roles. The new defenders run their own prepared implementation with fresh identities, keys, credentials and challenges. Reference attack work remains available until the common submission deadline.

An early breach does not eliminate your team. You may repair before the freeze and still earn full core defence credit.

## How marks and competition points work

### Academic assessment

| Component | Weight | Assessment |
|---|---:|---|
| Attack score A | 40% | Five challenges, each worth 12 points for a verified reference attack and 8 for reproducing it on a fresh equivalent target |
| Defence score D | 40% | Five challenges, each worth 10 points for legitimate functionality and 10 for rejecting the corresponding malicious cases |
| Individual understanding I | 20% | Explain a trace, identify the trust assumption and predict the effect of a small change |

Each score is out of 100. **Your academic mark = 0.40 A + 0.40 D + 0.20 I.** Team members share A and D; I is individual. An accessible equivalent to an oral/practical check can be arranged through the teaching team.

Protection credit requires the corresponding legitimate operation to work. Rejecting every request or stopping your node cannot earn those protection points. Defences face fixed and fresh hidden referee cases, even if the opposing team makes no effective attack.

Attack reproduction must adapt to fresh keys, identities and values. An old flag or a repeated success against the same instance is not a new method or additional credit. Screenshots and self-reported success messages do not replace referee-observed evidence.

### Leaderboard and awards

The core total is A + D, out of 200. Two competition-only bonuses bring the maximum to 220:

- **Live attack: 10 points** for at least one verified breach of the opponent's frozen network using a fresh final-window challenge. Further breaches do not increase the bonus.
- **Live defence: 10 points** if no final-window attack succeeds, every scheduled authorized newcomer joins and completes a protected operation on time, at least 80% of legitimate service checks succeed, and all fixed final security tests pass.

Awards recognize best attackers (A plus live attack bonus), best defenders (D plus live defence bonus), and best overall team. Equal totals share a placing. These bonuses do not change your academic mark.

The scoreboard distinguishes reference and live successes and shows legitimate service levels. Defence scores remain provisional until final tests finish. Exact secrets and successful attack payloads are withheld until the relevant round closes, then explanatory traces show what happened.

## Rules and operational limits

Use only your assigned arena, synthetic game identities and supported application interfaces. You may inspect the supplied source, generate game keys, publish false game identities, and submit, modify, replay or reorder permitted application messages.

The game assumes a trusted course issuer, reliable underlying transport and uncompromised founders. Founder compromise, malicious founder quorums and distributed-consensus recovery are outside this assignment.

The pilot proposes these limits; the teaching team must confirm them before release:

| Activity | Proposed limit |
|---|---|
| Newcomer admission | 120 seconds after delivery of a complete legitimate request |
| Legitimate message or command | 10 seconds after delivery to a running node |
| Revocation grace period | 60 seconds after notice delivery |
| Attack requests | 5 requests per second per team, plus a published total allowance for each challenge |

## What to submit

Submit one team package containing:

1. Defensive code/configuration and a clean reset/run procedure.
2. Attack scripts or supported reproduction procedures, organized by the five challenges. State the target, required starting state, execution steps and expected referee evidence.
3. A compact diagram covering founder trust, newcomer admission, protected communication and revocation.
4. An evidence table containing the arena, round, challenge, target version and trace reference for each claimed result.
5. A concise explanation of one attack and its repair, including a remaining limitation.
6. Each student's contributions and any resource/AI-use declaration required by course policy.

Do not include private game keys in the report. Provide the supported key-generation/reset procedure instead. Each student must be able to explain the submitted work and predict a changed case. Follow the published course AI policy; this handout does not grant additional permission to use generated submitted answers.

## Release details to be supplied by the teaching team

Before this draft is assigned, students need a release sheet containing:

- Session dates, team/arena allocation, submission deadline, submission location and support contact.
- Arena URLs, access instructions, starter version, exact setup/run/reset commands and editable file/hook list.
- Credential/message formats, helper documentation, legitimate client examples and a working local or hosted check.
- Exact protected operations, permitted attack interfaces, challenge proof/submission procedures and trace export instructions.
- Confirmed time limits, total request allowances, final-freeze procedure and scoreboard access.
- Report format/length, individual assessment arrangements, applicable AI/resource policy and issue-reporting route.

