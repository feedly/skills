# OWASP factor scales, scoring arithmetic and severity matrix

Read this file before scoring anything. The option values here are the only
permitted scores. Do not invent intermediate values and do not interpolate.

## The sixteen factors

Every factor is scored 0 to 9 using these options exactly.

### LIKELIHOOD, threat agent factors

| Factor | Options and scores |
|---|---|
| Skill Level | no technical skills 1 \| some technical skills 3 \| advanced computer user 5 \| network and programming skills 6 \| security penetration skills 9 |
| Motive | low or no reward 1 \| possible reward 4 \| high reward 9 |
| Opportunity | full access or expensive resources required 0 \| special access or resources required 4 \| some access or resources required 7 \| no access or resources required 9 |
| Size | developers 2 \| system administrators 2 \| intranet users 4 \| partners 5 \| authenticated users 6 \| anonymous internet users 9 |

### LIKELIHOOD, vulnerability factors

| Factor | Options and scores |
|---|---|
| Ease of Discovery | practically impossible 1 \| difficult 3 \| easy 7 \| automated tools available 9 |
| Ease of Exploit | theoretical 1 \| difficult 3 \| easy 5 \| automated tools available 9 |
| Awareness | unknown 1 \| hidden 4 \| obvious 6 \| public knowledge 9 |
| Intrusion Detection | active detection in application 1 \| logged and reviewed 3 \| logged without review 8 \| not logged 9 |

### IMPACT, technical factors

| Factor | Options and scores |
|---|---|
| Loss of Confidentiality | minimal non-sensitive data disclosed 2 \| minimal critical data disclosed 6 \| extensive non-sensitive data disclosed 6 \| extensive critical data disclosed 7 \| all data disclosed 9 |
| Loss of Integrity | minimal slightly corrupt data 1 \| minimal seriously corrupt data 3 \| extensive slightly corrupt data 5 \| extensive seriously corrupt data 7 \| all data totally corrupt 9 |
| Loss of Availability | minimal secondary services interrupted 1 \| minimal primary services interrupted 5 \| extensive secondary services interrupted 5 \| extensive primary services interrupted 7 \| all services completely lost 9 |
| Loss of Accountability | fully traceable 1 \| possibly traceable 7 \| completely anonymous 9 |

### IMPACT, business factors

| Factor | Options and scores |
|---|---|
| Financial Damage | less than the cost to fix the vulnerability 1 \| minor effect on annual profit 3 \| significant effect on annual profit 7 \| bankruptcy 9 |
| Reputation Damage | minimal damage 1 \| loss of major accounts 4 \| loss of goodwill 5 \| brand damage 9 |
| Non-compliance | minor violation 2 \| clear violation 5 \| high profile violation 7 |
| Privacy Violation | one individual 3 \| hundreds of people 5 \| thousands of people 7 \| millions of people 9 |

## Which factors come from where

Six factors are scored from the threat reporting: Skill Level, Motive, Size,
Ease of Discovery, Ease of Exploit, Awareness. Where the reporting does not
support one of them, say so and carry it into the questions rather than
guessing.

Ten factors depend on the organization, not the threat, so the reporting
cannot answer them: Opportunity, Intrusion Detection, Loss of
Confidentiality, Loss of Integrity, Loss of Availability, Loss of
Accountability, Financial Damage, Reputation Damage, Non-compliance, Privacy
Violation. Score them from the user's org context if the answer is there,
otherwise ask.

## Scoring arithmetic

1. Calculate three figures, each rounded to one decimal place:
   - Likelihood = the mean of the eight likelihood factor scores.
   - Technical impact = the mean of the four technical impact scores.
   - Business impact = the mean of the four business impact scores.

   Do not average technical and business impact together. OWASP keeps them
   separate and treats business impact as the more important of the two.
   Round half up, so 6.25 becomes 6.3 and 7.25 becomes 7.3. Round once, at
   the end. Never round a factor score, and never round a part-calculated
   mean.

2. Convert each to a level: 0 to below 3 is LOW, 3 to below 6 is MEDIUM,
   6 to 9 is HIGH.

3. Read overall severity off the OWASP matrix, using likelihood and business
   impact. The questions collect the business impact factors directly from
   the organization, so that input is grounded and takes precedence. If any
   business impact factor had to be estimated rather than answered, use
   technical impact for the matrix instead and say so.

   | Impact | Likelihood LOW | Likelihood MEDIUM | Likelihood HIGH |
   |--------|----------------|-------------------|-----------------|
   | HIGH   | Medium         | High              | Critical        |
   | MEDIUM | Low            | Medium            | High            |
   | LOW    | Note           | Low               | Medium          |

4. Report the scores and the severity word separately and label them
   clearly. Present it as "Likelihood 6.4 / 9, technical impact 7.3 / 9,
   business impact 7.1 / 9, Severity: Critical", and state which impact
   figure drove the severity. Do not blend scores into a single composite
   number. OWASP does not define one, and inventing one makes the rating
   harder to defend.

5. Show the arithmetic in the appendix so any score can be traced back to a
   factor and a source.

6. The financial exposure band is not part of this arithmetic. It never
   enters a mean, a level or the matrix. It is read off one factor after the
   scoring is complete.

## Four-option handling for the question tool

Where an OWASP factor has five options and the question tool allows four:

- Loss of Confidentiality: merge the two options that both score 6 into one
  option reading "minimal critical, or extensive non-sensitive [6]".
- Loss of Availability: merge the two options that both score 5 into one
  option reading "minimal primary, or extensive secondary [5]".
- Loss of Integrity: offer 1, 3, 7 and 9, and state in the question text
  that "extensive but only slightly corrupt data [5]" is available via Other.
- Skill Level, if the reporting could not support it: offer 1, 3, 6 and 9,
  and state that "advanced computer user [5]" is available via Other.
- Size, if the reporting could not support it: merge the two options that
  both score 2 into one reading "developers or system administrators [2]",
  then offer 4, 6 and 9, and state that "partners [5]" is available via
  Other.