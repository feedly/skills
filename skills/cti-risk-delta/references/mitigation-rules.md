# Mitigation rules: how a factor is allowed to move

Produce two ratings. Each is a full OWASP rating in its own right, scored
against the same sixteen factors and read off the same matrix.

- **Risk, before CTI action:** as scored at Step 4.
- **Residual risk, after CTI actions taken or planned:** re-scored counting
  the actions the user confirmed as "Already taken" or "Planned and
  committed" at Step 5c.

## Rules for moving a factor

**1.** A factor may only move if a specific named action changes what that
factor's OWASP definition measures. Name the action next to every change.

**2.** These six factors describe the threat and the outside world, not your
defences. Never move them: Skill Level, Motive, Size, Ease of Discovery,
Ease of Exploit, Awareness. Holding them constant is what keeps the delta
honest.

**3.** These are the factors defensive action can move, and what moves them:

| Factor | What moves it |
|---|---|
| Opportunity | patching, removing exposure, segmentation, MFA, blocking infrastructure, virtual patching or WAF rules |
| Intrusion Detection | new detection content, log source onboarding, EDR coverage, a completed hunt, alerting that is actually reviewed |
| Loss of Confidentiality | DLP, encryption, access review, credential rotation, reducing what the targeted system can reach |
| Loss of Integrity | immutable or offline backups, change control, code signing, file integrity monitoring |
| Loss of Availability | tested failover, offline backups, redundancy, a rehearsed recovery playbook |
| Loss of Accountability | better logging and forensic retention, which makes the attacker more traceable and moves the score down |
| Financial Damage | cyber insurance, fraud controls, payment verification |
| Reputation Damage | a tested crisis communications plan, pre-agreed holding statements, a customer notification process |
| Non-compliance | regulator notification readiness, closing a control gap tied to this threat |
| Privacy Violation | data minimisation, shorter retention, tokenisation, reducing the records held |

Faster containment is deliberately absent from the Financial Damage row. It
is bought by detection work, which is already counted against Intrusion
Detection, and counting it twice is what makes a money figure indefensible.

**4.** One action moves a factor by one option on the OWASP scale, unless the
action removes the condition outright. Patching the vulnerable component out
of the estate can take Opportunity to 0. Two weak actions do not add up to a
big move. Financial Damage is the one exception to the "removes the
condition outright" clause: it may never move by more than one option in
total, across every action combined, because with loss bands attached one
option can be two orders of magnitude of money. Where more than one action
would move it, apply one option and list the rest in Appendix C as
supporting.

**4a.** An action moves exactly one business impact factor, and nothing may
be counted against both a likelihood factor and a business impact factor.
Where an action could be argued into two, name the one it moves, and record
the second in the same Appendix C row by writing the second factor in the
Score change cell as "None, see evidence". Do not give an action two rows. A
technical action that genuinely moves two technical factors, such as offline
backups against Integrity and Availability, is not covered by this rule and
may move both.

**5.** An action the user marked "Not planned", or a recommendation they
never confirmed, does not move residual risk. This rule is not negotiable,
and applying it is what makes the residual number credible.

**6.** Actions marked "Planned and committed" do move residual risk, because
the user has confirmed they will happen. Every one must carry that status
and a target date in Appendix C, so a reader can see how much of the
reduction is already banked and how much is still owed. A commitment with no
date is not a commitment. It moves nothing, and it is recorded in Appendix D
as "committed, no date given" rather than as Not planned. Where the
financial exposure band moved and the action that moved it is Planned rather
than Taken, the financial exposure section must say so in the same line as
the band.

**7.** Residual can never score higher than before CTI action on any factor.
If an action made something worse, that is a finding, not a score change.
Note it in the appendix.

**8.** If no action moves any factor, say so plainly. Residual equals the
before rating, and the honest finding is that the intelligence has not yet
been actioned.