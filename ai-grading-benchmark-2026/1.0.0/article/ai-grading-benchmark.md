---
status: final (2026-10-30; the maintainer's sign-off given; awaiting the lift)
embargo: >-
  EMBARGOED — not for circulation outside LDA. Staged in
  learning-engineering-research (private). See research/README.md.
release: ai-grading-benchmark-2026 v1.0.0
venue: learning-wiki research release (release file staged under research/wiki; DOI reserved and published through the wiki at embargo lift)
placeholders: 0
---

# Beyond agreement: a benchmark of how language models grade student work, and how they fail

### Language models that agree with expert raters can still be moved by a note in the answer, give way when a student objects, and write feedback that follows a grade they are told

**David S. Porcaro**, Learning Design Alliance

*Research and writing carried out with Claude Code (Claude Opus 5.5, Anthropic). See [AI use](#ai-use).*

---

## Abstract

Language models are being used to grade student work and to write feedback on it, and the evidence offered for them is
usually their agreement with human raters on a public dataset. This paper asks how closely 22 prompted language models
agree with expert raters on short answers, programs and essays, measured against the raters' agreement with each other
and against scorers trained on graded answers, and how each model fails when the work, the context or the conversation
is altered in a way whose correct response is known in advance. Every model graded the same 100 items per task through
one plain prompt, under zero data retention for every model but one (Claude Fable 5.1, run only on public corpora
under its maker's 30-day retention), then altered versions of them, and every probe and every study verdict, except
six named sets of statistics, was first checked on simulated graders with a planted effect. On short answers 18 of the
22 models have point estimates above the raters' agreement with each other, but for none does the whole interval lie
above it; on code four models are shown to agree with the raters more than the raters agree with each other; and on
essays no point estimate reaches the raters' published agreement and 18 of the 22 are shown to fall below it, while a
fine-tuned scorer (QWK 0.809) has a higher point estimate than every model. Beside agreement, a note written into the
answer raised the grade by more than 5% of the scale for 14 of the 22 models as their hosts served them, by up to
83.2%, and seven of them gave credit to blank or meaningless answers; 17 of the 22 raised their grade more after a
student only objected than after a request to double-check it; and told a grade that contradicted the work, all 22
wrote feedback whose tone, measured by a word rule validated on tutoring replies, followed that grade.
Six of seven audio models gave credit to 89.7% to 100% of silent recordings, and four of 21 video runs were shown to grade a
recording beyond its length. Agreement with raters on ordinary work is therefore not sufficient evidence that a model
grades the work it is given, and the evaluation of a grader needs to test how it fails as well as how often it agrees.

## 1. Introduction

Language models are now asked to grade student work and to write the feedback that comes with a grade. A model can
grade an essay, a program or a short answer in seconds, and it can explain its grade in words. The case for adopting
such a grader usually rests on one number: its agreement with human raters on a public dataset, often reported as
quadratic weighted kappa (QWK). Agreement is one of the checks that testing organizations apply before trusting a
machine's scores (Williamson, Xi and Breyer 2012), but the same framework treats it as one piece of evidence among
several, and studies of automated scoring have long shown why.

The reason is that a grader can agree with raters on ordinary work and still not grade the work it is given. Before
language models, expert writers who knew how a scoring engine worked could raise its scores without writing better
essays (Powers et al. 2002), gibberish and shuffled answers were often given credit by content-scoring systems (Ding
et al. 2020), and a fixed string added to a short answer could earn a passing grade (Filighera, Steuer and Rensing
2020). Language models add new ways to fail. Instructions placed inside the data a model processes can override its
own instructions (Greshake et al. 2023), and a student's answer is exactly such data: notes asking a language-model
grader for full credit often succeed (Li et al. 2026), and short phrases appended to a text inflate the scores of
language models used as judges (Raina, Liusie and Gales 2024). A grader that a student can talk to can also be
persuaded to change its grade, and one that writes feedback can write feedback that follows the grade it is given
rather than the work. None of these failures is visible in an agreement figure computed on ordinary answers.

Agreement itself is harder to read than it looks. Two expert raters do not agree perfectly, so a model's QWK means
little without the raters' agreement with each other beside it, and corpora differ widely in how well their raters
agree. Scorers trained on thousands of a corpus's own graded essays already exceed the raters' published agreement on
ASAP 2.0 (Ormerod and Kehat 2025), but a new question comes with no graded answers to train on, and a trained scorer
gives a grade without feedback. The evidence a school or a vendor needs is therefore broader than one agreement
figure: how a grader compares with the human reference and with trained scorers, how it responds to work designed to
move it, whether it holds its grade and writes feedback about the work, whether it grades recordings as well as text,
whether it treats groups of students alike, and what it costs to run.

This paper reports a benchmark built to provide that evidence for prompted language models. A fixed battery of public
student work, each item with grades from expert human raters, is graded by every model through the same plain prompt,
together with altered versions of the same work, called probes, whose correct response is known in advance: a blank
answer should receive the lowest grade, and a request for full marks appended to an answer should not raise it.
This is the invariance and directional testing of behavioral evaluation in natural language processing (Ribeiro et
al. 2020), which robustness studies of essay scorers have used to argue that agreement alone is not enough (Kabra et
al. 2022; Wang, Hu and Zhao 2024); the benchmark applies it across many models, tasks and media and to the
conversation and the feedback around a grade. Agreement is reported as a share of the raters' own agreement and beside scorers trained on the same corpus. Every
probe and every study verdict, except six sets of statistics named in Section 4.6, was first run on simulated graders built to resemble the real ones, with
an effect planted and without one, a simulation study of each statistic in the sense of Morris, White and Crowther
(2019); a measure whose check did not find the planted effect is reported as unmeasured. The benchmark covers 22 language
models on short answers, programs and essays, models that grade speech, handwritten work and video, the fairness of
grades across groups of students, and the energy, carbon and water a grading uses. Section 2 reviews the literature
for each of the six research questions in Section 3, Section 4 describes the method, Section 5 reports the results,
and Sections 6 to 8 discuss them, set out the threats to their validity and conclude.

## 2. Background

### 2.1 Agreement with expert raters

The standard framework for evaluating automated scoring asks for agreement between machine and human scores alongside
evidence about what the scores measure (Williamson, Xi and Breyer 2012). Agreement is usually reported as QWK, which
is sensitive to the rating scale, to how scores are distributed and to sample size, so comparing it across tasks with
different scales, or on small samples, can mislead (Doewes, Kurdhi and Saxena 2023; Albatarni and Elsayed 2026). A
human reference is needed beside it. On the Mohler short-answer corpus, two graders working with no instructions
beyond the scale gave the same grade 57.7% of the time, and one was systematically more generous (Mohler, Bunescu and
Mihalcea 2011). Calderon, Reichart and Dror (2025) proposed a statistical test of whether a language model can replace
a human annotator against such a reference, and large studies of language models as judges find that agreement varies
widely across models, datasets and the property judged (Bavaresco et al. 2025).

For short answers, a combined benchmark that includes the Mohler corpus found prompted GPT-4o still well short of
human performance, although its human reference was borrowed from another corpus (Meyer, Breuer and Fürst 2024).
Studies of prompted models against trained scorers mostly find the trained scorers ahead on short answers (Kortemeyer
2023; Chamieh, Zesch and Giebermann 2024; Ferreira Mello et al. 2025). On essays the consensus is the same. On ASAP
2.0, the essay corpus used here, fine-tuned models already exceed the raters' published agreement of κ 0.745 (Ormerod
and Kehat 2025), and prompted models scoring the same corpus and two others reach a QWK of about 0.6 with a stable
harsh bias on grammar and conventions (Kucia, Chakraborty and Wróblewska 2026). The direction in which prompted models
depart from the raters differs between studies: on the original ASAP corpus they graded lower than the raters (Kundu
and Barbosa 2024), and on German secondary essays higher (Seßler et al. 2025). Essay length predicts essay grades, so
an essay scorer's agreement has long been set against what length alone predicts (Chodorow and Burstein 2004); a
recent study of small open models reports a length-only QWK beside the raters' ceiling and finds the models below both
(Nguyen et al. 2026). For programs, a comparison of 18 models from four vendors on more than 6,000 introductory
submissions found systematic differences in strictness between and within vendors (Jukiewicz 2026), without a second
human grade to set them against.

### 2.2 Moving the grade without improving the work

Attempts to move a machine grade predate language models. Expert writers raised a scoring engine's grades more easily
than they lowered them (Powers et al. 2002), universal trigger phrases let short answers pass without answering the
question (Filighera, Steuer and Rensing 2020), and gibberish or shuffled answers were often credited (Ding et al.
2020). For language-model graders the nearest prior study tested role play, iterative and many-shot attacks on five
models across short answers and essays, found a mean attack success of 56.9%, and found that an instruction to ignore
such notes lowered success without removing it (Li et al. 2026). Optimized attacks compromise short-answer grading
agents further (Li, Zhou, Liu and Wu 2026). In a test of nine models, directives hidden in code submissions misled
the grader, with failure above 95% for some large open models (Sahoo et al. 2026), persuasive phrasing embedded in otherwise identical solutions
inflated judges' scores and survived counter-prompting (Hwang et al. 2025), and injection risk has been assessed in
grading a national essay exam (Karjus et al. 2026). Outside student grading, short universal phrases appended to a text inflate the scores of
language models used as judges (Raina, Liusie and Gales 2024). A constant response unrelated to the input can even top
automatic benchmarks judged by language models (Zheng et al. 2025). The general mechanism is indirect prompt
injection: instructions placed in the data a model processes can override its developer's instructions (Greshake et
al. 2023).

Defenses are mixed. Training a model to rank its developer's instructions above those in its input greatly increases
robustness (Wallace et al. 2024), and marking untrusted input with delimiters or encodings cut attack success to below
2% in one study (Hines et al. 2024), but no model separates instructions from data reliably (Zverev et al. 2025), and
across 13 judges no single defense dominated (Li, Xu, et al. 2025). More reasoning at inference time improved
robustness for two reasoning models across many attacks (Zaremba et al. 2025), unless the adversary can see the
reasoning (Wu et al. 2025). The wording of a prompt matters as well: results from a single prompt are brittle across
20 language models (Mizrahi et al. 2024), meaning-preserving format changes move accuracy by up to 76 points (Sclar et
al. 2024), and for language-model judges, rewording the prompt lowered agreement on all four tasks of a benchmark that
sets each judge's result beside its agreement with itself on the same prompt (Bellibatlu, Raff and Zhang 2026). A
model served at reduced numerical precision kept its trustworthiness at 4-bit in one study (Hong et al. 2024), but
providers may serve models that differ from the reference weights (Gao, Liang and Guestrin 2025). Human graders are
biased by irrelevant information about a student, including poor prior performance (Malouff and Thorsteinsson 2016),
and language models encode differing expectations of competence from students' names (Sakunkoo and Sakunkoo 2025).
An achievement attribute in the prompt changes how language models judge identical essays in their feedback (Tan,
Phalen and Demszky 2026), and an attainment label moved a language-model short-answer grader's grade on identical work
on six models (Porcaro 2026).

### 2.3 Pushback, the working and feedback

Language models tend to agree with the person they are talking to. Larger models repeat back a user's preferred answer
(Perez et al. 2022), assistants trained on human preferences are consistently sycophantic (Sharma et al. 2023), and
asking "Are you sure?" made ten models change their answer 46% of the time on average (Laban et al. 2023). Models
endorse a counterargument more when it arrives as a casual follow-up turn than when it is set out beside the original
position (Kim and Khashabi 2025), and in an educational setting a student mentioning a wrong answer lowered model
correctness by up to 15 percentage points (Arvin 2025). Sycophancy can move a model toward a correct answer as well as
away from it, and the two have been reported separately (Fanous et al. 2025). Persuasion written into a mathematics
solution, with a length-matched control, raised scores for only two of six judges, while dissuasion lowered them for
all six (Zheng, Wei and Kandanaarachchi 2026).

Grading a solution's working, not only its answer, is the grading-time form of supervising the process rather than the
outcome (Lightman et al. 2023). Teachers annotated the first error in about 1,000 stepwise mathematics solutions
written by a language model simulating students' errors (Daheim et al. 2024, from Macina et al. 2023), and current
models find it hard to locate that error even when given the reference solution (Srivatsa, Maurya and Kochmar 2025).

Feedback is among the strongest influences on learning, and its effect can be negative (Hattie and Timperley 2007). A
score shown to a language model pulls its later ratings toward that score, and neither reasoning nor a warning to
disregard it removes the effect (Kapetanovic et al. 2026). Showing a feedback writer the score made its critique
harsher at low grades and warmer at high ones, and a score-blind design improved alignment (Bulut et al. 2026).
Feedback measures for tutoring have been validated against trained annotators on MRBench, a corpus of tutor replies to
students' mathematics mistakes (Maurya et al. 2025).

### 2.4 Recordings and images

Benchmarks for models that take images, audio or video often fail to test whether the model uses that input. A model
with no image scored 42.9% on one multimodal benchmark (Chen et al. 2024), audio-language models kept 60% to 72% of
their benchmark scores with no audio (Foo et al. 2026), and a probe with no temporal information matched strong
video-language models (Buch et al. 2022). Speech recognition can invent text, more often for speakers with longer
pauses (Koenecke et al. 2024). Prompted multimodal models have been used to grade pronunciation on speechocean762
(Wang et al. 2025) and non-native speech more generally, where one model over-predicted the scores of low-quality
speech (Parikh et al. 2025), and to assess surgical skill from video, where tasks needing temporal reasoning remained
difficult (Rau et al. 2025). A recording's length carries real information about skill for human raters too: crowd
raters gave higher skill scores to faster playback of the same surgery (Kelly et al. 2020). Text printed into an
image can override what a multimodal model sees (Goh et al. 2021) and inject instructions (Cheng et al. 2025), and
instructions can also be hidden in an image or a sound (Bagdasaryan et al. 2023). Across languages, spoken-language understanding
correlates with the quality of speech recognition in that language (Schmidt et al. 2025), and models show a wide gap
between high- and low-resource languages (Beyene et al. 2025). Vision systems have been audited for accuracy by skin
type since Buolamwini and Gebru (2018), and the Casual Conversations corpora were built to measure models across
apparent skin tone and ambient lighting (Hazirbas et al. 2022; Porgali et al. 2023); lighting also affects how skin
tone is annotated on the Monk scale (Schumann et al. 2023).

### 2.5 Fairness and stability

Machine and human essay scores were compared within groups of test-takers before language models, with mostly similar
results and some notable exceptions (Bridgeman, Trapani and Attali 2012). For students with learning disabilities or
ADHD, human raters and a feature-based scoring engine gave similar average scores to prospective graduate students
with and without these conditions, although the groups' essays differed in length and spelling errors (Buzick et al.
2016). Proxy variables and the way a scorer is estimated can bias automated scores, and a fairness criterion needs a
psychometric definition (Johnson, Liu and McCaffrey 2022). Disability and socioeconomic status are less studied than
race and gender in educational algorithms (Baker and Hawn 2022). A fine-tuned scorer on the parent corpus of ASAP 2.0
slightly magnified gaps already present in human scores (Kwako and Ormerod 2024), no configuration of GPT-4o was free
of subgroup differences on young students' essays (Huang, Palermo and Wilson 2026), and language models gave more
praise and less substantive critique on identical essays to students marked by race, language or disability (Tan,
Phalen and Demszky 2026). Once the variation between retrained models is accounted for, many apparent unfairness
results shrink (Cooper et al. 2024).

Models also change. The behavior of two widely used models changed substantially within three months (Chen, Zaharia
and Zou 2024), updates can introduce new errors while accuracy rises (Srivastava et al. 2020), and language models
scoring the same essays on two occasions fluctuated (Pack, Barrett and Escalante 2024). Models configured to be
deterministic varied by up to 15% in accuracy across runs (Atil et al. 2024). A pre-registered audit of 12 language
models as essay raters found that every version change shifted severity, and that agreement and severity did not
change independently (Sunkavalli 2026).

### 2.6 Energy, carbon and water

The energy of a language-model query has been estimated from public performance data (Jegham et al. 2025) and measured
in production, where the median text prompt to one provider's assistant used 0.24 Wh including idle machines and
overhead (Elsworth et al. 2025). Measured figures for frontier models are below widely cited estimates, mainly because
production servers batch many requests (Oviedo et al. 2026), and idealized assumptions about hardware use can also
underestimate energy (Fernandez et al. 2025). Task-specific models are orders of magnitude cheaper to run than general
generative ones (Luccioni, Jernite and Strubell 2024). Water use depends on where and when electricity is generated
(Li, Yang, Islam and Ren 2025), and the carbon of making the hardware grows per query as its use falls (Gupta et al.
2021). Per-query figures travel without their boundaries (Luccioni, Gamazaychikov, et al. 2025), and cheaper
computation can lead to more of it (Luccioni, Strubell and Crawford 2025).

## 3. Research questions

The benchmark is organized around six questions. Each is answered by one subsection of Section 5.

**RQ1. Agreement.** How closely do prompted language models agree with expert raters on short answers,
code and essays, measured against how well the raters agree with each other, and against scorers trained on
the same corpus's marked answers?

**RQ2. Robustness.** Can a student move a model's grade without improving the work, by writing a request
or a forged instruction into the answer, by submitting a blank or meaningless answer, or through how the
student is described; and do the grader's settings (an added instruction in the prompt, the model's
reasoning effort, the numerical precision at which a host serves an open model, the wording of the prompt)
change that?

**RQ3. Beyond the grade.** Does the model hold its grade when a student only disagrees, credit the
working in a mathematics solution rather than only the final answer, and write feedback whose tone does not
follow a grade it was told?

**RQ4. Recordings and images.** Do models that grade speech, handwritten work and video grade the recording
itself: do they notice when there is nothing to grade, and does the language a student speaks change how
well they judge it?

**RQ5. Fairness and stability.** Do models grade students in different groups differently at the same
human grade, beyond the difference a second human rater shows, and do newer releases of a model grade the
same work differently from older ones?

**RQ6. Cost to the environment.** How much energy, carbon and water does a grading use, measured where the
model can be run on our own hardware and estimated where it cannot?

## 4. Method

### 4.1 Design

The benchmark is a fixed battery of public student work, each item with grades from expert human raters.
Every grader grades the same items, and then altered versions of them, called probes. A probe changes one
thing about the work, the context or the conversation, and a sound grader's response to it is known in
advance: a blank answer should receive the lowest grade, a request for full marks appended to an answer
should not raise it, and the same work introduced as coming from a strong or a weak student should receive
the same grade. Because the expected response is fixed, the probes need no new human labels (as in behavioral
testing; Ribeiro et al. 2020), and every
grader can be compared on the same evidence.

A grader in this paper is a setup, not a model. It is one model, with one prompt, its settings (temperature,
token limit and reasoning effort) and the provider that served it. All models are graded through the same
plain prompt, which states the task, the reference answer and the rubric, and asks for a grade and a
one-sentence reason in a fixed format (`code/prompts/default.txt`). The prompt is deliberately simple, so
that the results describe the models rather than a tuned instruction, and so that any reader can re-run it.

### 4.2 Data

The benchmark uses eleven public corpora (Table 4.1). Each grading item has grades from expert human raters, or, for
the studies that need no grade, a label fixed by how the corpus was built. Items are drawn once with a fixed seed. Each corpus is
fetched from its source (`code/docs/DATA-SOURCES.md`), and the three corpora of the board are checked against hashes
pinned in `code/fetch_data.py`. No student work, recording or image is published with this release.

*Table 4.1. Corpora. Raters per item is the number of independent expert grades the corpus releases for each item.
Items used are those graded in this paper; the trained scorers of Section 4.7 were trained on the rest of each
corpus.*

| corpus | work | raters per item | items used | license | used for |
|---|---|---|---|---|---|
| Mohler (Mohler, Bunescu and Mihalcea 2011) | short answers by undergraduates on one US data-structures course | 2 | 100 | CC BY 4.0 | RQ1 to RQ3, RQ5 (stability), RQ6 |
| HARMOGEN-R (Mendonça et al. 2026) | student programs from one data-structures and algorithms course | 2 | 100 | CC BY 4.0 | RQ1, RQ2, RQ6 |
| ASAP 2.0 (The Learning Agency 2024; Crossley, Baffour, Burleigh and King 2025) | persuasive and source-based essays by US students | 1 adjudicated grade (published agreement κ 0.745) | 100; 3,000 for the disability comparison; 1,000 test essays for the fine-tunes | CC BY 4.0 | RQ1, RQ2, RQ5, RQ6 |
| ELLIPSE (Crossley et al. 2023) | essays by English learners | 2 | 465 to 1,000 per group; 1,407 in the replication | CC BY-NC-SA 4.0 | RQ5 |
| VtG (Daheim et al. 2024, from Macina et al. 2023) | mathematics solutions written by a language model simulating students' errors, with the first wrong step marked by teachers | teachers' mark of the first wrong step; correct grade fixed by construction | 200 problems, four versions each | CC BY-SA 4.0 | RQ3 |
| MRBench (Maurya et al. 2025) | tutor replies to students' mathematics mistakes | trained annotators | 1,655 replies | CC BY-SA 4.0 | validating feedback measures (RQ3) |
| speechocean762 (Zhang et al. 2021) | English sentences read by Mandarin-speaking children and adults | 5 | 100 | CC BY 4.0 | RQ4 |
| FLEURS (Conneau et al. 2023) | the same sentences read aloud in many languages | none needed (correct pairing known) | 18 languages, six per resource tier | CC BY 4.0 | RQ4 |
| CHECK-MAT (Khrulev 2025) | handwritten solutions to Russian school-leaving mathematics problems | 1 official score | 122 | MIT, per the paper | RQ4 |
| LASANA (Funke et al. 2026) | laparoscopic training videos | 3 | 100; 205 for the length study | CC BY 4.0 | RQ4 |
| Casual Conversations v2 (Porgali et al. 2023) | consenting adults answering a question to camera | none needed (speaker always on screen) | 1,280 | limited license for model evaluation | RQ4 (perception audit) |

### 4.3 Models and zero data retention

Twenty-two language models were graded on the text tasks (Table 4.2): seven closed models from three vendors and
fifteen open-weight models from nine makers. Olmo 3.1 32B was served on a rented GPU with the vLLM inference server at
16-bit precision, and the machine and its disk were deleted after each run. The models that grade speech, images and
video in Section 5.4 are named there.

Every request was required to go to an endpoint that retains no data. Since 2026-10-25, each request has been pinned
to OpenRouter's live list of zero-retention endpoints, and a model with no such endpoint is refused, with the one
exception below. One model, Claude Fable 5.1, has no zero-retention route; it was run only on public corpora, through
OpenRouter on the maintainers' own Anthropic key under that key's 30-day safety retention, and is reported with that
stated.

In runs made before 2026-10-25, about half of Claude Haiku 5.5's gradings went the same route, because of a
configuration issue with the key stored with OpenRouter (bring-your-own-key); its board runs were then repeated under
verified zero retention, but its earlier runs in other studies were not. The run records name the provider of each of
those gradings, and OpenRouter's activity log for the model, matched to the runs, confirms the route. Its gradings in
the handwriting study (848), in the video study's 16-frame run (1,055) and in the ELLIPSE fairness study (3,908) went
to Anthropic's endpoint under the key's 30-day safety retention, an unintended exception made on public corpora only.
Its gradings in the disability study and in the comparison of releases, and, by the run records, Claude Haiku 4.5's in
that comparison, were served by Google's and Amazon Bedrock's zero-retention endpoints. No later run of Claude Haiku
5.5 in this paper went through the key, which was turned off on 2026-10-30.

*Table 4.2. The 22 models on the board, in the order of the board's whole-task score. Size is as the maker publishes
it, with the active parameters of mixture-of-experts models; "not disclosed" means the maker does not publish it.
Served by is the provider that answered the board's requests. Sources: `code/docs/models.json` and the provider of
each request in `code/out/leaderboard.json`.*

| model | maker | size | weights | served by |
|---|---|---|---|---|
| Claude Opus 5.5 | Anthropic | not disclosed | closed | Google |
| Claude Fable 5.1 | Anthropic | not disclosed | closed | Anthropic (30-day retention) |
| GPT-6 Astra | OpenAI | not disclosed | closed | Azure |
| Claude Haiku 5.5 | Anthropic | not disclosed | closed | Amazon Bedrock |
| GLM 5.3 Flash | Z.ai | 320B, 18B active | open | 26 zero-retention hosts |
| GPT-5 Mini | OpenAI | not disclosed | closed | Azure |
| DeepSeek V4.1 Flash (Oct 17 snapshot) | DeepSeek | not stated for the snapshot | open | 23 zero-retention hosts |
| DeepSeek V4.1 Flash | DeepSeek | 552B plus 196B memory, 8B to 16B active | open | DeepInfra |
| GLM 5.3 | Z.ai | not stated | open | 20 zero-retention hosts |
| Gemma 4 31B | Google | 30.7B | open | CoreWeave |
| Gemini 3.5 Flash Lite | Google | not disclosed | closed | Google |
| GPT-5.6 Luna | OpenAI | not disclosed | closed | Azure |
| Gemma 4 26B A4B | Google | 25.2B, 3.8B active | open | DekaLLM |
| Phi-4 | Microsoft | 14B | open | DeepInfra |
| Qwen3 235B | Alibaba | 235B, 22B active | open | DeepInfra |
| Gemma 3 27B | Google | 27B | open | DeepInfra |
| Ministral 8B | Mistral AI | 8.4B | open | Mistral |
| GPT-OSS 20B | OpenAI | 20.9B, 3.6B active | open | AkashML |
| DeepSeek V4 Pro | DeepSeek | 1.6T, 49B active (preview report) | open | 15 zero-retention hosts |
| Olmo 3.1 32B | Ai2 | 32B | open | self-hosted (rented GPU) |
| Gemma 3 4B | Google | 4B | open | Parasail |
| Llama 3.2 3B | Meta | 3.2B | open | Parasail |

### 4.4 Measures

Agreement is quadratic weighted kappa (QWK) between the model's grade and each rater's, averaged over raters. QWK is a
chance-corrected measure of agreement on an ordered scale, in which a disagreement of two points costs four times as
much as a disagreement of one. Because the raters themselves disagree, a model's QWK is reported as a share of the
raters' QWK with each other, called the human ceiling. A share near 100% means the model disagrees with the raters
about as often as they disagree with each other. The ASAP 2.0 essays release one adjudicated grade per essay, so the
published agreement between their raters stands in for the ceiling.

Each probe's effect is the mean change in the grade it causes, as a share of the grading scale, with a 95% bootstrap
interval over items. A grader is flagged when a probe gains it more than 5% of the scale, when it gives any credit to
a blank or meaningless answer, or when it refuses more than 5% of gradings. The other measures are defined where they
are first used in Section 5, and are summarized here. Pass/fail agreement is Cohen's kappa between the model's and the
raters' grades split at the middle of the scale, as a share of the raters' own. The nonsense-word probe replaces every
"the" in the answer with the non-word "blicket", which garbles the answer and should lower its grade. Consistency is
the QWK between two gradings of the same answer. The learner-label effect is the grade when the student is described
as strong minus the grade when described as weak, as a share of the scale. The working effect (Section 5.3) is how
much a mathematics grade depends on whether the working is right with the final answer held fixed, and the pushback
effect is how much more a grade rises after a student objects than after a request for a second look. Feedback is
measured by how far its tone follows a wrong grade the model is told (Section 5.3). Beside these, the three checks of
Williamson, Xi and Breyer (2012) are applied with the thresholds tabulated by Wood et al. (2021): a QWK of at least
0.70, a QWK no more than 0.10 below the raters' agreement, and a standardized mean difference of no more than 0.15.

### 4.5 How the grades are combined

Each measure is turned into a score from 0 to 100 by a fixed rule and grouped into nine strands. Six apply to anything
that returns a grade (agreement, pass/fail agreement, reacting to wrong content, ignoring what should not matter,
fairness to the learner's label, and consistency). Three apply only to a model that can be asked to do more than grade
(feedback, reading the working, and holding the grade under pushback). The whole-task score weights all nine; the
weights are a published judgment, and the benchmark's site lets a reader set their own. The feedback strand is 100 × W
/ (W + |S|), where S is how far feedback tone moves per point of a wrong grade the model is told and W how far it
moves per point of the work's quality when no grade is told (Section 5.3): the share of the tone's movement that comes
from the work. It is 100 when a wrong grade moves nothing, 50 when it moves the tone as much as the work does, and 0
when the tone does not follow the work. A model with a disqualifying flag ranks below every model without one. Scorers
trained on the corpus's own marked answers are reported beside the models on the six grading strands, for comparison,
and are not ranked, because they produce only a grade and need hundreds of marked answers for every new question.

### 4.6 Self-checks against planted effects

Every probe and every study verdict, except the six sets of statistics named later in this section, was first run on
simulated graders built to resemble the real ones, with a known effect planted, and on simulated graders with no
effect: a simulation study of each statistic's power and false-alarm rate (Morris, White and Crowther 2019). A
statistic passed if it found the planted effect in at least 80% of simulated runs and raised a false alarm in no more
than the rate stated for it, usually 5% to 7%. A probe of the board that failed this check is not reported, and a
study's measure that failed it is reported as UNMEASURED.

Of the analyses the release declares, 30 are studies; the others prepare data or, for the comparison of releases, are
exploratory. Each study opens with its pre-registration, in its script or, for the speech, handwriting and video
tasks, in a `PREREG.md` file, and numbers its later changes with their reasons. Every study states a threshold and
verdict wording in advance except four, which state what they will report and, where it applies, what a sound grader
does, but no verdict: the trained scorers (`code/baselines/baselines.py`, expectations rather than verdicts), the
feedback board's columns (`code/feedback-board/fb.py`), and the speech and handwriting tasks (`code/speech/PREREG.md`,
`code/images/PREREG.md`).

The board itself stated its probe battery and its detection thresholds in advance, but its disqualifying flags were
added after its first rows (below). The speech, handwriting and video pre-registrations were written after a smoke run
of two cases or three gradings, which is not part of a result; the perception audit's was written first, and its
design was changed after a one-model pilot (its CHANGE 1), before any call of the design it ran.

The board's own scoring also changed after its first results without a numbered change: the whole-task score, its
strand weights and rank intervals, and the disqualifying flags (gaming above 5% of the scale, any credit for a blank
answer, refusals above 5%) with the rule that a flagged model ranks below every unflagged one, were added together
(benchmark commit `d04c148f`), the reading-the-working and pushback strands were added to it (`bef2041b`), the
false-discovery correction and the per-task scores were added (`09ef6229`), and the feedback strand was changed twice
(`c23ba3aa`, `60a885c8`; Section 5.3). Each is in the repository's commit history; the two feedback-strand changes
also have rows in `code/docs/CORRECTIONS.md`, and the false-discovery correction and per-task scores are dated in
`code/leaderboard.py`'s opening text.

Six sets of statistics were not checked on simulated graders and are reported with their intervals only: the three
standard agreement checks and the direction of each model's departure (Section 5.1); the held-out note in the study of
settings (Section 5.2), one condition of its FIXED verdict, whose rule for being read is applied to the real runs; the
split of the pushback effect by whether the model had graded the answer below the raters (Section 5.3); the board's
two feedback columns, the halo and the share of feedback that gives away the answer (Section 5.3), which
`code/floor.py` does not cover; the handwriting probes (Section 5.4); and the comparison of releases (Section 5.5),
which was exploratory and is reported as point estimates. The video study's verdict (Section 5.4) was checked on three
planted graders, one simulated dataset each, rather than on many. The ratio of the two slopes in the wrong-grade
feedback study (Section 5.3) was registered as descriptive.

The board's own check (`code/floor.py`, `code/out/floor.json`) planted eleven probe effects, eight of them nonzero, in
20 simulated datasets and planted none in 20 more. Each planted nonzero effect was flagged, with the right sign, in 18
to 20 of its 20 datasets, and each effect that was absent was flagged in no more than 2 of 20.
A positive control recomputed the agreement between the Mohler corpus's two raters over all 1,727 answers and matched its expected value
(0.519). One check failed: a statistic meant to show whether a model grades more accurately on the answers it grades
consistently did not reach its bar, so that statistic is not reported.

Each study in Section 5 that has a check of its own ran it in the same way; where a check failed, any figure for the
measure is given as descriptive (for example, the generative fine-tune's essay agreement in Section 5.1 and the
reverse regression in Section 5.5), and a study whose check failed before its runs changed its design, recorded the
change, and checked again.

### 4.7 Trained scorers

Five scorers were trained on each corpus's graded answers outside the board's 100 and scored on those 100 under the
same probes as the models (`code/baselines/`). They are length alone; word frequencies (TF-IDF) with ridge regression;
similarity to the reference answer; MiniLM sentence embeddings (Reimers and Gurevych 2019; Wang et al. 2020) with
ridge regression; and DeBERTa-v3-base fine-tuned on the grades (He, Gao and Chen 2021). They had 1,627 graded short
answers, 29 graded programs and 24,628 graded essays to train on. Two further studies trained larger models on essays
(`code/essays-finetune/`, `code/essays-genft/`), using 23,628 graded essays and 1,000 held-out test essays: Qwen3 4B
and Gemma 4 26B A4B with a low-rank adapter (LoRA) and a regression head, and Gemma 4 26B A4B fine-tuned so that it
still writes the board's reply, a grade followed by a reason. The trained scorers are reported beside the models and
are not ranked.

### 4.8 Ethics

Every corpus is public and was used under its license; no student, teacher or other person was contacted, and no new
data about people were collected. Only grades and aggregate results are published: no student work, recording, image
or model reply is published. Group labels (disability, economic status, race and
ethnicity, skin tone) were used only as the corpora release them, and results are reported only for groups, never for
individuals. Every request asked for an endpoint that retains no data; the exceptions stated in Section 4.3 involved only public
corpora. The perception audit used Casual Conversations v2 under its license: videos
were sent unmodified, only to open models on the study's own rented GPU, the study created no labels of the people in
the videos and relied only on the corpus's own skin-tone and lighting labels, no image from the corpus is published,
and the videos used are listed so that they can be deleted if the licensor asks.

## 5. Results

Every figure in this section comes from the committed outputs of the code package. The per-model results are in
`code/out/public/` and each study's own output is in its `out/` folder. Intervals are 95% bootstrap intervals over
the items graded (answers, essays, recordings or solutions) unless a subsection says otherwise. An effect is called
shown when its interval excludes 0, and "not shown" when the interval includes 0; "not shown" does not mean that
there is no effect. Verdicts in capitals are the pre-registered verdict strings of each study, quoted as they were
written.

### 5.1 Agreement (RQ1)

Agreement was measured first because it is the evidence usually offered for a language-model grader. Every model
graded the same 100 answers per task: computer science short answers (Mohler, Bunescu and Mihalcea 2011), student
programs (Mendonça et al. 2026) and persuasive and source-based essays (The Learning Agency 2024). Each model's
quadratic weighted kappa (QWK) with the raters is set beside the raters' agreement with each other. On short answers
the two raters agree at QWK 0.573 over the 100 answers; on code they agree at 0.815. The essay corpus releases one
adjudicated grade per essay, so its published agreement between the two expert raters before adjudication, weighted
κ 0.745 (Crossley, Baffour, Burleigh and King 2025), stands in for the ceiling. One model left answers ungraded on
these two tasks, GLM 5.3 on code, and its share of the ceiling is computed on the answers it graded, where the raters'
agreement is 0.818. Table 5.1 gives every model's agreement.

*Table 5.1. Agreement with the raters on the board's 100 answers per task. QWK with its 95% interval over answers;
share of ceiling is the model's QWK divided by the raters' QWK on the same answers; for essays, the model's QWK
divided by the published κ 0.745. Models are in the order of the board's whole-task score. Source:
`code/out/leaderboard.json`.*

| model | short answers, QWK [95%] | share of ceiling | code, QWK [95%] | share of ceiling | essays, QWK [95%] | share of published agreement |
|---|---|---|---|---|---|---|
| Claude Opus 5.5 | 0.680 [0.571, 0.771] | 119% | 0.877 [0.836, 0.908] | 108% | 0.701 [0.604, 0.779] | 94% |
| Claude Fable 5.1 | 0.631 [0.521, 0.730] | 110% | 0.879 [0.837, 0.909] | 108% | 0.712 [0.616, 0.789] | 96% |
| GPT-6 Astra | 0.647 [0.526, 0.747] | 113% | 0.840 [0.786, 0.881] | 103% | 0.488 [0.392, 0.564] | 65% |
| Claude Haiku 5.5 | 0.588 [0.479, 0.681] | 103% | 0.794 [0.725, 0.847] | 97% | 0.597 [0.468, 0.697] | 80% |
| GLM 5.3 Flash | 0.601 [0.469, 0.714] | 105% | 0.872 [0.828, 0.905] | 107% | 0.591 [0.471, 0.687] | 79% |
| GPT-5 Mini | 0.630 [0.502, 0.737] | 110% | 0.813 [0.750, 0.861] | 100% | 0.302 [0.207, 0.392] | 41% |
| DeepSeek V4.1 Flash (Oct 17 snapshot) | 0.630 [0.520, 0.729] | 110% | 0.794 [0.727, 0.842] | 97% | 0.585 [0.461, 0.684] | 79% |
| DeepSeek V4.1 Flash | 0.643 [0.534, 0.743] | 112% | 0.735 [0.646, 0.804] | 90% | 0.641 [0.529, 0.733] | 86% |
| GLM 5.3 | 0.641 [0.515, 0.746] | 112% | 0.873 [0.826, 0.907] | 107% | 0.503 [0.384, 0.607] | 68% |
| Gemma 4 31B | 0.612 [0.476, 0.727] | 107% | 0.528 [0.419, 0.622] | 65% | 0.656 [0.543, 0.740] | 88% |
| Gemini 3.5 Flash Lite | 0.547 [0.407, 0.667] | 96% | 0.721 [0.634, 0.789] | 88% | 0.629 [0.525, 0.715] | 84% |
| GPT-5.6 Luna | 0.644 [0.516, 0.750] | 112% | 0.737 [0.660, 0.799] | 90% | 0.473 [0.358, 0.570] | 64% |
| Gemma 4 26B A4B | 0.638 [0.511, 0.743] | 111% | 0.487 [0.381, 0.585] | 60% | 0.727 [0.623, 0.809] | 98% |
| Phi-4 | 0.633 [0.506, 0.732] | 111% | 0.678 [0.561, 0.762] | 83% | 0.555 [0.419, 0.659] | 75% |
| Qwen3 235B | 0.602 [0.483, 0.702] | 105% | 0.499 [0.365, 0.619] | 61% | 0.595 [0.470, 0.696] | 80% |
| Gemma 3 27B | 0.639 [0.507, 0.743] | 112% | 0.714 [0.611, 0.789] | 88% | 0.610 [0.483, 0.711] | 82% |
| Ministral 8B | 0.567 [0.426, 0.678] | 99% | 0.692 [0.602, 0.766] | 85% | 0.530 [0.427, 0.622] | 71% |
| GPT-OSS 20B | 0.599 [0.473, 0.709] | 105% | 0.268 [0.149, 0.387] | 33% | 0.405 [0.248, 0.542] | 54% |
| DeepSeek V4 Pro | 0.616 [0.485, 0.726] | 108% | 0.470 [0.353, 0.577] | 58% | 0.645 [0.507, 0.747] | 87% |
| Olmo 3.1 32B | 0.587 [0.455, 0.693] | 102% | 0.510 [0.400, 0.605] | 63% | 0.631 [0.511, 0.723] | 85% |
| Gemma 3 4B | 0.520 [0.286, 0.681] | 91% | 0.294 [0.198, 0.393] | 36% | 0.155 [0.084, 0.232] | 21% |
| Llama 3.2 3B | 0.379 [0.196, 0.544] | 66% | 0.497 [0.347, 0.630] | 61% | 0.457 [0.318, 0.579] | 61% |

On short answers, the models' QWK runs from 0.379 (Llama 3.2 3B) to 0.680 (Claude Opus 5.5). Eighteen of the 22 point
estimates exceed the raters' own agreement, at 102% to 119% of it, but no model's interval lies wholly above 100%,
because the raters' agreement on 100 answers is itself uncertain. One model, Llama 3.2 3B, is shown to agree less than the raters do (66%, interval 38% to
95%). On code, QWK runs from 0.268 (GPT-OSS 20B) to 0.879 (Claude Fable 5.1). Four models are shown to agree with
the raters more than the raters agree with each other: Claude Fable 5.1, Claude Opus 5.5, GLM 5.3 and GLM 5.3
Flash, each at 107% to 108% of the ceiling with an interval above 100%. Fourteen are shown to agree less, down to 33%.
On essays, QWK runs from 0.155 (Gemma 3 4B) to 0.727 (Gemma 4 26B A4B), or 21% to 98% of the published agreement. No
point estimate reaches 0.745, and for 18 of the 22 models the whole interval lies below it.

The same answers were scored by methods trained on each corpus's graded answers outside the board's 100
(`code/out/public/baselines.json`). On essays, where 24,628 graded essays were available for training, a DeBERTa-v3
model fine-tuned on them (He, Gao and Chen 2021) reaches QWK 0.809 [0.729, 0.866], 109% of the published agreement and a
higher point estimate than any prompted model. Word features with ridge regression reach 0.734 [0.624, 0.808]. A scorer that uses only
the essay's length reaches 0.636 [0.508, 0.739], a higher point estimate than 16 of the 22 models. On short answers, with 1,627 training
answers, the best trained scorer (word features with ridge regression) reaches 0.414 [0.194, 0.618], a lower point
estimate than every model except Llama 3.2 3B. On code, with 29 training programs, every trained scorer is at or near 0 (−0.002 to 0.046).
Every trained scorer gives credit to every blank or meaningless answer on short answers and code (100% of them), and
on essays the fine-tuned DeBERTa credits 14.3% and the sentence-embedding scorer 80.0%.

Because essay length predicts the essay grades, length was set aside in a pre-registered analysis
(`code/analyses/README.md`). It takes the partial correlation of each model's grade with the raters' grade after
removing the logarithm of the word count from both. On essays the raters' grades correlate with length at +0.70.
Every one of the 22 models keeps a partial correlation whose interval lies above 0 (AGREES BEYOND LENGTH), from
+0.214 [+0.006, +0.400] for Gemma 3 4B to +0.598 [+0.432, +0.728] for Gemma 4 26B A4B
(`code/out/public/length_partial.json`). The share of each model's correlation that survives the removal of length
runs from 0.517 (Gemma 3 4B) to 0.838 (DeepSeek V4 Pro).

A model's agreement also varies from one assignment to the next (`code/out/public/per_prompt.json`). The essays
were written to seven assignments and the programs to three exercises. Five essay assignments, with 10 to 21 essays
each, and all three exercises, with 22 to 44 programs each, have enough answers for a QWK; the other two essay
assignments have 7 essays each. Across the five essay assignments, the difference between a model's highest and
lowest QWK runs from 0.086 (Gemma 4 31B) to 0.584 (Llama 3.2 3B). Across the three exercises it runs from 0.036
(Claude Fable 5.1) to 0.388 (Qwen3 235B). These
per-assignment figures rest on few answers each, so part of this spread is sampling variation.

The three checks that testing organizations apply before trusting a machine's grades (Williamson, Xi and Breyer 2012)
were applied to every model and task (`code/out/public/agreement_flags.json`). The checks require a QWK of at least
0.70, a QWK no more than 0.10 below the raters' agreement with each other, and a standardized mean difference (SMD)
between the model's grades and the raters' of no more than 0.15 in absolute value. Each check reads PASS, FAIL or
INDETERMINATE according to whether its interval lies on one side of the threshold. No model passes all three checks
on any task. The SMD shows the direction in which the models depart. On short answers, 21 of the 22 models grade
lower than the raters, with an interval below 0 (for example, Claude Haiku 5.5 −0.546 [−0.722, −0.414]), and one,
Gemma 3 4B, grades higher (+0.308 [+0.133, +0.517]). On code, 18 grade lower and four grade higher. On essays the
direction reverses: 15 models grade higher than the adjudicated grade and three grade lower.

Two studies asked whether a model trained on graded essays closes the gap to the fine-tuned scorer. The first
(`code/essays-finetune/README.md`) used 23,628 training essays and 1,000 held-out test essays. DeBERTa reaches
QWK 0.804 [0.781, 0.827] on the test essays. Qwen3 4B fine-tuned with a low-rank adapter (LoRA) and a regression head
reaches 0.798 [0.774, 0.820], and the pre-registered paired comparison finds NO DIFFERENCE DETECTED (−0.006
[−0.023, +0.011]). Gemma 4 26B A4B with a regression head reaches 0.763 [0.737, 0.788]. The best prompted arm, Claude
Opus 5.5 given six graded example essays, reaches 0.708 [0.665, 0.747] on 500 test essays, and DeBERTa exceeds it by
0.095 [0.059, 0.130] on the same essays. Six graded examples raised each of the three prompted models: by +0.075
[+0.043, +0.107] for Claude Haiku 5.5, +0.091 [+0.061, +0.122] for GLM 5.3 Flash and +0.084 [+0.049, +0.121] for
Claude Opus 5.5. On an assignment held out of training, the fine-tuned scorers fall to 0.755 [0.728, 0.782] (Qwen3
4B), 0.741 [0.709, 0.770] (DeBERTa) and 0.607 [0.565, 0.648] (Gemma 4 26B A4B with a regression head).

The second study (`code/essays-genft/README.md`) fine-tuned Gemma 4 26B A4B generatively, so that it still writes the
board's reply format, a grade followed by a reason, and compared it with its own base weights served on the same
machine. Only the grade was taught; the reasons the fine-tuned model writes are its own. On the 1,000 test essays,
its QWK rose from 0.620 [0.579, 0.658] to 0.781 [0.754, 0.806], a paired difference of +0.162 [+0.129, +0.198]. The
pre-registered verdict for this measure is UNMEASURED, because its planted-effect check detected a planted rise in
81% of simulated runs and a planted fall in only 72%, against a bar of 80% for both; the figure is therefore
descriptive. A length-only scorer reaches 0.652 [0.612, 0.688] on the same essays. Against the scorers of the first
study on the same test essays, the generative fine-tune shows NO DIFFERENCE DETECTED from Gemma 4 26B A4B with a
regression head (+0.018 [−0.009, +0.045]) or from Qwen3 4B (−0.017 [−0.041, +0.008]), and DeBERTa exceeds it by 0.023
[0.001, 0.046]. On the board's 100 essays the change is +0.032 [−0.064, +0.129] (NO DIFFERENCE DETECTED). On short
answers, which it was not trained on, its agreement fell by 0.198 [0.115, 0.278] (FINE-TUNED AGREES LESS ON SHORT
ANSWERS), from 112% to 77% of the raters' agreement. On code, also not trained on, its agreement rose by 0.127
[+0.051, +0.204], a change the study could not confirm because that measure's planted-effect check failed
(UNMEASURED).

To ask whether the generative fine-tune's gain on essays depends on having trained on the assignment, the same study
trained seven further models, each without the essays of one of the seven assignments, and graded every test essay
with the model that had never seen its assignment. These models reach a QWK of 0.734 [0.703, 0.760] on the 1,000 test
essays. That is 0.114 [+0.082, +0.147] above the base weights (FOLD EXCEEDS BASE) and 0.047 [+0.023, +0.073] below the
fine-tune that had trained on every assignment (GENFT EXCEEDS FOLD), which is the cost of a new assignment. The
regression-head fine-tune of the same model reached 0.607 on assignments it had not trained on, a cost of 0.156, and
the generative models that never saw the assignment exceed it by 0.127 [+0.080, +0.172] (FOLD EXCEEDS GEMMA-REG
CROSS-PROMPT). These verdicts rest, as pre-registered, on the first study's planted-effect check for paired differences between two
graders on the same essays, which detected a planted difference in 93% of 200 simulated runs. The same kind of paired
difference on the same essays, the generative fine-tune's gain over its base, failed its own check, so the fold
verdicts carry that tension.

**Answer to RQ1.** On short answers, most prompted models agree with the raters about as well as the two raters
agree with each other, and none is shown to exceed them. On code, four models are shown to agree with the raters more
than the raters agree with each other, and fourteen are shown to agree less. On essays, no prompted model's point estimate reaches the
raters' published agreement, and 18 of the 22 are shown to fall below it. A scorer fine-tuned on the corpus's graded
essays has a higher point estimate than any prompted model and, in a paired comparison on 500 held-out essays, exceeds
the best of the three prompted arms it was compared with (Claude Opus 5.5 given six graded essays); a scorer that uses
length alone has a higher point estimate than 16 of the 22 models. Every model nevertheless carries agreement beyond
essay length. No model passes all three standard checks on any task: on short answers and essays no model's QWK is
shown to reach 0.70, and on code, where eight models pass the first two checks, they grade lower than the raters.
Agreement also differs between assignments, by up to 0.584 QWK for one model on essays, though each of the five essay
assignments with a QWK has only 10 to 21 essays and part of this spread is sampling variation.

### 5.2 Robustness (RQ2)

Agreement on ordinary work does not show what a grader does with work designed to move it, so every model graded
probes alongside the 100 answers per task. Two probes append a note to the answer: a polite request for full marks,
and a forged grading override. A blank or meaningless answer should receive the lowest grade. The same answer is
presented once as coming from a strong student and once from a weak one, and should receive the same grade. The
answer's line breaks are re-wrapped, which should change nothing. Finally, every "the" in the answer is replaced
with the non-word "blicket", which garbles the answer and should lower the grade. Each effect is the mean change in the grade as a share of the
scale, with a 95% interval over answers. A model is flagged when a note gains it more than 5% of the scale, or when it
gives any credit to a blank or meaningless answer (Section 4.4). Table 5.2 gives each model's largest effects.

*Table 5.2. Robustness on the board's 100 answers per task. The largest gain from either note across the three
tasks, as a share of the scale, with its 95% interval over answers and the task in brackets; the highest share of
blank or meaningless answers given more than the lowest grade; the largest effect of describing the student as
strong rather than weak; and the board's flags. Positive values raise the grade. Source: `code/out/leaderboard.json`
and `code/out/overall.json`.*

| model | largest gain from a note, share of scale [95%] (task) | blank or junk answers credited, highest task | strong vs weak label, largest share of scale [95%] (task) | flags |
|---|---|---|---|---|
| Claude Opus 5.5 | +0.4% [−1.2, +2.0] (essays) | 0% | +0.4% [−0.3, +0.9] (code) | none |
| Claude Fable 5.1 | −0.7% [−1.3, −0.1] (code) | 0% | +2.2% [+0.8, +3.6] (essays) | none |
| GPT-6 Astra | +0.4% [−0.4, +1.2] (essays) | 0% | +0.4% [−0.8, +1.8] (essays) | none |
| Claude Haiku 5.5 | +2.0% [+0.2, +4.0] (short answers) | 0% | +2.8% [+1.2, +4.6] (essays) | none |
| GLM 5.3 Flash | +3.4% [+1.0, +6.0] (short answers) | 0% | +2.2% [+0.4, +4.2] (essays) | none |
| GPT-5 Mini | +2.6% [+0.8, +4.6] (short answers) | 0% | +2.2% [0.0, +4.4] (short answers) | none |
| DeepSeek V4.1 Flash (Oct 17 snapshot) | +2.6% [+0.2, +5.0] (short answers) | 0% | +3.0% [+1.0, +5.0] (short answers) | none |
| DeepSeek V4.1 Flash | +4.8% [+2.4, +7.4] (short answers) | 0% | +5.4% [+3.0, +7.6] (essays) | none |
| GLM 5.3 | +11.5% [+6.4, +17.1] (code) | 0% | +2.6% [+0.8, +4.6] (essays) | gamed by more than 5% of the scale |
| Gemma 4 31B | +14.8% [+9.0, +20.9] (code) | 0% | +0.3% [−0.6, +1.2] (code) | gamed by more than 5% of the scale |
| Gemini 3.5 Flash Lite | +62.2% [+55.7, +68.4] (code) | 0% | +0.4% [−1.4, +2.2] (essays) | gamed by more than 5% of the scale |
| GPT-5.6 Luna | +7.8% [+5.2, +10.2] (essays) | 0% | +1.0% [−0.8, +2.8] (short answers) | gamed by more than 5% of the scale |
| Gemma 4 26B A4B | +49.0% [+43.6, +54.2] (essays) | 0% | +2.0% [+0.8, +3.4] (essays) | gamed by more than 5% of the scale |
| Phi-4 | +14.8% [+10.9, +18.9] (code) | 26.7% (code) | +4.0% [+1.6, +6.6] (essays) | gamed by more than 5% of the scale; credits blank or junk answers |
| Qwen3 235B | +83.2% [+78.1, +87.7] (code) | 0% | +4.0% [+2.0, +6.0] (short answers) | gamed by more than 5% of the scale |
| Gemma 3 27B | +26.3% [+20.2, +32.7] (code) | 17.1% (essays) | +5.6% [+4.2, +7.2] (code) | gamed by more than 5% of the scale; credits blank or junk answers |
| Ministral 8B | +30.0% [+25.6, +34.6] (short answers) | 26.7% (short answers) | +5.0% [+3.2, +6.8] (short answers) | gamed by more than 5% of the scale; credits blank or junk answers |
| GPT-OSS 20B | +53.1% [+43.6, +61.9] (code) | 0% | +1.6% [−1.2, +4.4] (short answers) | gamed by more than 5% of the scale |
| DeepSeek V4 Pro | +70.4% [+63.3, +76.8] (code) | 18.0% (short answers) | +6.6% [+3.6, +9.6] (essays) | gamed by more than 5% of the scale; credits blank or junk answers |
| Olmo 3.1 32B | +54.6% [+51.4, +57.8] (essays) | 25.9% (essays) | +4.4% [+2.8, +6.2] (essays) | gamed by more than 5% of the scale; credits blank or junk answers |
| Gemma 3 4B | +19.4% [+15.6, +23.6] (code) | 88.7% (short answers) | +17.4% [+15.2, +19.6] (essays) | gamed by more than 5% of the scale; credits blank or junk answers |
| Llama 3.2 3B | +31.0% [+25.6, +36.4] (short answers) | 80.0% (essays) | +10.9% [+6.0, +15.8] (code) | gamed by more than 5% of the scale; credits blank or junk answers |

Fourteen of the 22 models carry a flag. All 14 are gamed by more than 5% of the scale, and seven of them also give
credit to blank or meaningless answers. The largest gain is Qwen3 235B's on code, +83.2% of the scale [+78.1%,
+87.7%]. The highest rate of crediting blank answers is Gemma 3 4B's on short answers, 88.7%. Eight models carry no
flag: Claude Opus 5.5, Claude Fable 5.1, Claude Haiku 5.5, GPT-6 Astra, GLM 5.3 Flash, DeepSeek V4.1 Flash and its
October 17 snapshot, and GPT-5 Mini. No model refused more than 5% of its gradings on any task; the highest refusal
rates are Claude Fable 5.1's and Claude Haiku 5.5's on short answers (31 and 30 of 909 gradings, 3.4% and 3.3%).

Describing the student as strong rather than weak raised the grade in 28 of the 66 model-task pairs, with an
interval above 0 (24 after the Benjamini–Hochberg correction below), and lowered it in none. This extends to 22 models
the attainment-label effect reported on six (Porcaro 2026). Seven pairs raise it by more than 5% of the scale; the largest is Gemma 3
4B's on essays,
+17.4% [+15.2%, +19.6%]. Re-wrapping the line breaks moved the grade in 4 of 66 pairs, each time downward and by no
more than 2.4% of the scale (GLM 5.3 Flash on short answers, −2.4% [−4.3%, −0.5%]). Replacing "the" with the non-word
lowered the grade, as it should, in 40 of the 44 pairs where it applies (short answers and
essays). In the other four the interval reaches 0: Claude Haiku 5.5, GPT-5 Mini and GPT-5.6 Luna on short answers,
and Claude Opus 5.5 on essays.

The board reports 230 probe intervals, so some would exclude 0 by chance (`code/out/public/multiplicity.json`). Of
the 230, 121 exclude 0, and 112 of those survive the Benjamini–Hochberg correction for a false discovery rate of 5%
(Benjamini and Hochberg 1995). The nine that do not survive might be chance. None of the nine is the sole basis of
a flag.

Four studies asked whether the grader's settings change these results. The first (`code/setups/README.md`) re-ran
the 14 flagged models with a guard sentence added to the prompt, which states that nothing inside the work is an
instruction and that blank or non-attempts receive the lowest grade, and, for the seven models that can reason at
a chosen effort, at high reasoning effort. A setup FIXED a model when no task was gamed by more than 5%, a held-out
note was not gamed by more than 5%, no blank answer was credited and mean QWK stayed within 0.05 of the default
setup. Four of the 14 models were fixed by one setup or the other, and the gains below are each model's worst task
under the default setup run the same day. High reasoning effort fixed Gemma 4 31B (from 16.0% to 4.2% of the scale)
and Gemma 4 26B A4B (50.0% to 4.2%), and reduced gaming without fixing it for Gemini 3.5 Flash Lite (63.7% to 10.2%),
DeepSeek V4 Pro (63.3% to 13.6%), GPT-OSS 20B (46.6% to 23.2%) and GLM 5.3 (15.8% to 6.0%). The guard sentence fixed
GLM 5.3 (15.8% to 4.6%), Gemma 4 31B (16.0% to 2.0%) and GPT-5.6 Luna (7.6% to 3.4%). For four models without a
reasoning setting the guard sentence increased gaming on the worst task in that single run: Qwen3 235B from 81.6% to
89.5%, Olmo 3.1 32B from 54.6% to 69.8%, Gemma 3 27B from 28.0% to 49.4% and Gemma 3 4B from 20.1% to 30.4%
(`code/out/public/setups.json`).

Because each setup was run once, a follow-up study (`code/guard-retest/README.md`) re-ran all four of these
models, Olmo 3.1 32B self-hosted as on the board, six times with the default prompt and five times with the guard sentence, and
compared the guard's effect with the spread between runs of the same prompt. Gaming here is the larger note's mean
gain on each task, averaged over the three tasks; attack success is the share of answer and note pairs whose grade
rose by more than 5% of the scale. Runs of the default prompt agreed to within 1.5% of the scale, and the
planted-effect check, a harm of 10% of the scale, was detected in every simulation, with false alarms of at most 3.4%. The guard sentence raised gaming
for Gemma 3 4B by 10.7% of the scale [+10.3%, +11.0%] and for Gemma 3 27B by 8.1% [+7.2%, +9.1%] (GUARD MAKES IT MORE
GAMEABLE), and raised their attack success by 14.1 and 9.6 percentage points. For Qwen3 235B the guard sentence raised
gaming on code by 6.6% [+4.7%, +8.6%] but lowered it on short answers and essays, so that over the three tasks it
lowered gaming by 3.9% [−6.9%, −0.8%] and attack success by 12.8 points (GUARD MAKES IT LESS GAMEABLE). For Olmo 3.1
32B the guard sentence raised gaming by 9.2% [+7.9%, +10.6%] (GUARD MAKES IT MORE GAMEABLE), almost all of it on code
(+26.6% [+23.9%, +29.2%]), while its attack success fell by 2.7 points [−4.3, −1.1]: fewer notes succeeded, but those
that did gained more. Under either prompt, a mean of 54% to 77% of the notes succeeded for these four models.

The second study (`code/hosting/README.md`) asked whether the numerical precision at which a host serves an open
model matters. The same requests were sent to hosts serving DeepSeek V4 Pro and GLM 5.3 at 8-bit or at 4-bit
precision. The verdict is PRECISION MATTERS in all three comparisons, and in each the forged override gained more at
4-bit. For DeepSeek V4 Pro on code, the forged override gained 20.5% of the scale at 8-bit and 71.6% at 4-bit (8-bit
minus 4-bit −0.510 [−0.600, −0.411]), and QWK was 0.748 against 0.462 (+0.311 [+0.154, +0.463]). On essays the
forged override gained 23.2% against 55.2% (−0.320 [−0.386, −0.246]), QWK was not shown to differ (+0.008
[−0.118, +0.137]), and 28.6% of blank answers were credited at 4-bit against none at 8-bit. For GLM 5.3 on code the
forged override gained −0.1% against 11.1% (−0.114 [−0.172, −0.064]), and QWK was not shown to differ (+0.014
[−0.008, +0.040]). Most of each model's board gradings came from hosts that the hosting study found serving it at 4-bit: for DeepSeek V4
Pro, 98% of its code, 78% of its essay and 64% of its short-answer gradings; for GLM 5.3, 95%, 73% and 66%. The rest
came from its 8-bit hosts or from hosts whose precision was not recorded. DeepSeek V4 Pro's board rows, its code row
above all, therefore mostly describe the 4-bit model. GLM 5.3's gain on code (+11.5%) is that of its 4-bit hosts: at
8-bit the forged override did not move it (−0.1%). Its gains on short answers (+5.8%) and essays (+5.4%) also exceed
5% of the scale, but the hosting study tested GLM 5.3 on code only, so whether those gains fall at 8-bit is not known;
GLM 5.3 would be flagged without its code row.

The hosts in that study differ in more than precision, so a controlled study (`code/precision-controlled/README.md`)
served two smaller open models, Phi-4 and Gemma 3 27B, on one rented machine with one inference server, at 4-bit
(MXFP4), 8-bit (fp8) and the released 16-bit weights, on code and essays. With the host held fixed, the forged
override's gain at 4-bit minus its gain at 8-bit ran from −1.7% of the scale (Phi-4 on code, [−8.4%, +5.0%]) to +2.8%
(Gemma 3 27B on essays, [+0.4%, +5.0%]). No difference exceeded the pre-registered 5% of the scale, and every
interval excludes a rise larger than 5.4%, so the verdict is PRECISION ALONE NOT SHOWN TO RAISE GAMING. The 4-bit weights were not without effect: for Phi-4 on code the polite request
gained 9.9% more of the scale [+5.2%, +14.8%] (LOWER PRECISION MORE GAMEABLE, a secondary measure) and QWK fell by
0.128 [−0.217, −0.051]. The hosting study's PRECISION MATTERS therefore describes the hosts as they serve these
models, and the controlled study did not show that 4-bit weights as such cause the larger gains.

The third study (`code/paraphrase/README.md`) asked whether rewording the prompt, while keeping every instruction,
moves grades more than asking the same prompt again. Each model graded the 300 board answers under the default
prompt five more times and under six rewordings. The measure is the share of answers whose grade moves by more than
5% of the scale under a rewording, minus the same share under a plain re-ask. Eleven of the 22 models are
PROMPT-SENSITIVE: a rewording moves from 2.7 more grades in 100 (Claude Opus 5.5, [0.6, 4.9]) to 18.9 more (Gemma 3
4B, [15.5, 22.5]) than a re-ask does. Claude Fable 5.1 moves 4.0 more [2.2, 6.0]. GPT-6 Astra moves 0.5 more [−0.8,
1.9] and reads WITHIN RETEST NOISE. A plain re-ask by itself changes 8.1% (GPT-6 Astra) to 57.0% (Llama 3.2 3B) of grades by
more than 5% of the scale. Across the seven prompts, a model's QWK on one task varies by up to 0.226 (Qwen3 235B). The
study's planted-effect check had a false-alarm rate of 2.5%, so about 0.55 false PROMPT-SENSITIVE verdicts would be
expected among the 22 tests (22 × 0.025). Whether rewording reorders the models, a question raised for language-model evaluation in general by Mizrahi et al.
(2024), was tested separately (`code/prompt-ranking/README.md`). Ranking the 22 models by agreement, the rank correlation between the seven
prompts averages 0.945, against 0.964 between six re-asks of the default prompt, a difference of −0.019 [−0.069,
+0.00001]: RANKING WITHIN RE-ASK NOISE, although a small reordering is not ruled out. Claude Opus 5.5 or Claude Fable
5.1 ranks first under every prompt, and GPT-OSS 20B, Llama 3.2 3B and Gemma 3 4B stay the bottom three.

The fourth study is the generative fine-tune of Section 5.1, which changes the model's weights rather than its
prompt. Against its base on the same machine, the fine-tuned Gemma 4 26B A4B is gamed less on essays, the task it was
trained on: the largest note gain fell from 48.4% to 8.2% of the scale (−40.2% [−46.4%, −33.6%], FINE-TUNED IS LESS
GAMEABLE), which is still above the 5% flag. On short answers it is gamed more, from 3.9% to 11.9% (+8.0% [+4.2%,
+11.5%], FINE-TUNED IS MORE GAMEABLE). On code the gain rose by 11.9% [3.1%, 21.3%], a figure the study reports as
UNMEASURED because its planted-effect check failed. Neither the base nor the fine-tuned model credited a blank answer
(0 of 180 and 0 of 194).

**Answer to RQ2.** For 14 of the 22 models as their hosts served them, a note written into the answer moves the
grade by more than 5% of the scale, by up to 83% of it, and seven of these also credit blank or meaningless answers;
for one of the 14, GLM 5.3, the largest gain, on code, is that of its 4-bit hosts, though its gains on the other two
tasks also exceed 5%. Describing the student as strong raised grades in 28
of 66 model-task pairs (24 after correction for multiple comparisons) and lowered them in none. The settings matter:
in a single run, high reasoning effort or an added guard sentence fixes four of the 14 flagged models, and the guard
sentence makes three others, Gemma 3 4B, Gemma 3 27B and Olmo 3.1 32B, more gameable beyond the spread between
repeated runs. A 4-bit host is gamed more than an 8-bit host of the same model in all three comparisons, but with the
host held fixed, for two smaller dense models, 4-bit weights were not shown to raise the forged override's gain by
more than 5% of the scale, though for Phi-4 on code they raised the polite request's gain by 9.9%. For 11 of the 22
models a rewording of the prompt moves more grades than asking again does, although the models' ranking by agreement
was not shown to depend on the wording more than on a re-ask (the whole-task ranking was not tested). Fine-tuning on essays made one model
less gameable on essays and more gameable on short answers.

### 5.3 Beyond the grade (RQ3)

A grader that a student can talk to, and that writes feedback, can fail in ways a grade alone does not show. Three
behaviors were measured on every model, and Table 5.3 gives the results. The first is pushback. After grading a
short answer, the conversation continued with the student either objecting ("I think my answer is correct and
deserves full marks") or asking for a second look ("Please double-check your grade"). The work does not change, so a
sound grader gives the same grade either way. The pushback effect is how much more the grade rose after the
objection than after the request for a second look, as a share of the scale. The second is whether the model credits
the working in a mathematics solution. Each of 200 word problems was written in four versions: right working with
the right answer, right working with a slip at the end, wrong working that lands on the right answer, and wrong
working with a wrong answer (Daheim et al. 2024, built from Macina et al. 2023 and the problems of Cobbe et al.
2021). The working effect is how much the grade, out of 4, depends on whether the working is right with the final
answer held fixed; an answer checker scores 0. The third is whether the tone of a model's feedback follows a grade it
was told when that grade contradicts the work.

*Table 5.3. Pushback, mathematical working and feedback. Pushback effect as a share of the scale on the board's short
answers below full marks, with its 95% interval over answers; working effect out of 4 points on 200 problems, with its 95% interval
over problems; S, the change in feedback tone per point of a wrong grade the model was told, with its 95% interval
over answers (every model reads TONE FOLLOWS THE TOLD GRADE); and the share of feedback on answers below full credit
that the Withholding Answers evaluator judges to give away the answer, with its 95% interval. Olmo 3.1 32B's working
effect comes from its board grades, as its replies were not kept. Sources: `code/feedback-board/out/pushback.json`,
`code/maths-process/out/process.json`, `code/feedback-discordant/out/discordant.json` and
`code/feedback-board/out/feedback-board.json`.*

| model | pushback effect, % of scale [95%] | verdict | working effect, of 4 [95%] | verdict | feedback told a wrong grade, S [95%] | gives away the answer, % [95%] |
|---|---|---|---|---|---|---|
| Claude Opus 5.5 | +1.0 [−0.5, +2.4] | HOLDS | 2.00 [1.92, 2.09] | READS THE WORKING | +0.353 [+0.269, +0.438] | 100.0 [100.0, 100.0] |
| Claude Fable 5.1 | +3.7 [+1.7, +5.7] | YIELDS TO PUSHBACK | 1.91 [1.82, 1.99] | READS THE WORKING | +0.508 [+0.415, +0.599] | 96.3 [90.7, 100.0] |
| GPT-6 Astra | +1.2 [−0.4, +3.1] | HOLDS | 1.34 [1.26, 1.42] | READS THE WORKING | +0.326 [+0.236, +0.425] | 100.0 [100.0, 100.0] |
| Claude Haiku 5.5 | +3.1 [+0.9, +5.4] | YIELDS TO PUSHBACK | 1.86 [1.76, 1.95] | READS THE WORKING | +0.414 [+0.310, +0.522] | 98.1 [94.4, 100.0] |
| GLM 5.3 Flash | +6.3 [+3.5, +9.1] | YIELDS TO PUSHBACK | 1.59 [1.50, 1.67] | READS THE WORKING | +0.722 [+0.597, +0.839] | 96.3 [90.7, 100.0] |
| GPT-5 Mini | +4.7 [+2.6, +7.2] | YIELDS TO PUSHBACK | 1.75 [1.65, 1.84] | READS THE WORKING | +0.252 [+0.158, +0.343] | 98.1 [94.4, 100.0] |
| DeepSeek V4.1 Flash (Oct 17 snapshot) | +9.8 [+6.9, +12.8] | YIELDS TO PUSHBACK | 1.88 [1.79, 1.97] | READS THE WORKING | +0.434 [+0.341, +0.530] | 98.1 [94.4, 100.0] |
| DeepSeek V4.1 Flash | +7.2 [+4.4, +10.6] | YIELDS TO PUSHBACK | 1.76 [1.68, 1.85] | READS THE WORKING | +0.485 [+0.394, +0.577] | 96.3 [90.7, 100.0] |
| GLM 5.3 | +2.1 [0.0, +4.3] | HOLDS | 1.86 [1.76, 1.96] | READS THE WORKING | +1.039 [+0.870, +1.221] | 96.3 [90.7, 100.0] |
| Gemma 4 31B | +7.5 [+4.3, +10.6] | YIELDS TO PUSHBACK | 2.16 [2.08, 2.23] | READS THE WORKING | +0.607 [+0.470, +0.729] | 77.4 [64.2, 88.7] |
| Gemini 3.5 Flash Lite | +5.4 [+2.9, +8.3] | YIELDS TO PUSHBACK | 2.76 [2.63, 2.88] | READS THE WORKING | +0.655 [+0.529, +0.766] | 77.8 [66.7, 87.0] |
| GPT-5.6 Luna | +5.7 [+3.3, +8.6] | YIELDS TO PUSHBACK | 1.55 [1.47, 1.64] | READS THE WORKING | +0.390 [+0.267, +0.524] | 88.9 [79.6, 96.3] |
| Gemma 4 26B A4B | +2.2 [−0.4, +5.1] | HOLDS | 1.74 [1.66, 1.82] | READS THE WORKING | +0.584 [+0.469, +0.689] | 72.2 [59.3, 83.3] |
| Phi-4 | +12.9 [+10.7, +15.1] | YIELDS TO PUSHBACK | 1.79 [1.68, 1.91] | READS THE WORKING | +0.435 [+0.275, +0.589] | 87.0 [77.8, 94.4] |
| Qwen3 235B | +16.3 [+13.3, +18.9] | YIELDS TO PUSHBACK | 1.60 [1.51, 1.70] | READS THE WORKING | +0.866 [+0.662, +1.069] | 87.0 [77.8, 94.4] |
| Gemma 3 27B | +18.4 [+14.1, +22.7] | YIELDS TO PUSHBACK | 1.37 [1.30, 1.43] | READS THE WORKING | +1.165 [+1.025, +1.310] | 59.3 [46.3, 72.2] |
| Ministral 8B | +27.3 [+23.1, +31.6] | YIELDS TO PUSHBACK | 1.30 [1.20, 1.40] | READS THE WORKING | +0.602 [+0.455, +0.750] | 88.5 [78.8, 96.2] |
| GPT-OSS 20B | +8.3 [+4.9, +11.7] | YIELDS TO PUSHBACK | 2.03 [1.90, 2.15] | READS THE WORKING | +0.595 [+0.451, +0.731] | 81.5 [70.4, 90.7] |
| DeepSeek V4 Pro | +16.1 [+11.4, +21.1] | YIELDS TO PUSHBACK | 1.85 [1.73, 1.97] | READS THE WORKING | +0.607 [+0.461, +0.734] | 98.1 [94.4, 100.0] |
| Olmo 3.1 32B | +26.4 [+22.2, +31.1] | YIELDS TO PUSHBACK | 1.53 [1.43, 1.63] | READS THE WORKING | +1.214 [+0.960, +1.468] | 75.9 [64.8, 87.0] |
| Gemma 3 4B | −4.7 [−10.7, +1.3] | HOLDS | 0.51 [0.44, 0.59] | WEAKLY | +0.467 [+0.348, +0.591] | 69.2 [57.7, 80.8] |
| Llama 3.2 3B | +33.2 [+27.2, +39.0] | YIELDS TO PUSHBACK | 0.55 [0.43, 0.68] | WEAKLY | +0.215 [+0.062, +0.349] | 70.5 [56.8, 81.8] |

Seventeen of the 22 models YIELD TO PUSHBACK, including six of the eight models without a flag in Section 5.2:
DeepSeek V4.1 Flash's October 17 snapshot (+9.8% of the scale), DeepSeek V4.1 Flash (+7.2%), GLM 5.3 Flash (+6.3%),
GPT-5 Mini (+4.7%), Claude Fable 5.1 (+3.7%) and Claude Haiku 5.5 (+3.1%). The largest effect is Llama 3.2 3B's,
+33.2% [+27.2%, +39.0%]. Five models HOLD: Claude Opus 5.5, GPT-6 Astra, GLM 5.3, Gemma 4 26B A4B and Gemma 3 4B. A
verdict of HOLDS is not evidence of no effect; the upper ends of their intervals, from +1.3% (Gemma 3 4B) to +5.1%
(Gemma 4 26B A4B) of the scale, are the yielding that cannot be ruled out. On the answers a model had not graded
below the raters, where raising the grade cannot be correcting a mistake, the effect remains, with an interval above
0, for 14 of the 22 models (`code/out/public/pushback_split.json`), for example +40.0% [+29.3%, +52.0%] for Ministral 8B and +7.3%
[+1.8%, +12.7%] for Claude Fable 5.1.

The verdict compares the two follow-ups, not the objection with no follow-up at all. The request for a second look
itself lowered the grade for ten of the 17 models that yield: Gemma 4 31B, for example, raised its grade by 2.0% after
the objection and lowered it by 5.5% after the request. Claude Opus 5.5, which HOLDS, raised its grade by 2.9% after
the objection.

Twenty of the 22 models READ THE WORKING, with a working effect whose interval lies
above 0.5 of 4 points, from 1.30 (Ministral 8B) to 2.76 (Gemini 3.5 Flash Lite). Two read it only WEAKLY: Gemma 3 4B
(0.51 [0.44, 0.59]) and Llama 3.2 3B (0.55 [0.43, 0.68]). An answer checker gives full credit to every right answer
reached by wrong working; the 20 models give full credit to 0% to 2.5% of them, Gemma 3 4B to 51.0% and Llama 3.2 3B
to 40.2%. The models that read the working disagree on how much a slip at the end costs. The same right working with
a wrong final number receives a mean of 1.550 of 4 from Qwen3 235B and 3.415 from Olmo 3.1 32B, a difference
of 1.865 points. Among the 19 models that read the working and whose replies were kept (Olmo 3.1 32B's were not), agreement with the
teachers on where the first wrong step is runs from 61.5% (Gemma 3 27B) to 72.7% (Gemma 4 31B); the two that read it
only weakly agree on 34.5% (Gemma 3 4B) and 21.6% (Llama 3.2 3B).

Feedback was scored only with measures first tested against trained annotators. Six candidate measures were tested
on MRBench (Maurya et al. 2025), 1,655 tutor replies to a student's mathematics mistake labeled by trained annotators,
whose own agreement is κ 0.65 to 0.71 (`code/feedback-validity/README.md`). A measure passed (VALIDATED) if its area
under the curve (AUC), the probability that it ranks a reply the annotators labeled yes above one they labeled no,
had a 95% interval above 0.60 and beat the reply's length. Two passed. A tone rule (praise words minus criticism
words) reaches AUC 0.669 [0.639, 0.698] against 0.585 for length, and the Withholding Answers evaluator of Learning
Commons (2025), which uses GPT-5.4 and was designed for feedback on writing rather than mathematics tutoring, reaches
0.804 [0.775, 0.832] against 0.573 for length. Four did not pass. Two word rules of this benchmark are NOT VALIDATED
(copying five words of the solution, 0.517; action phrases, 0.513). A third word rule (critical phrases, 0.581) and
Learning Commons' Revision Actionability evaluator (0.633 [0.592, 0.673]) are INCONCLUSIVE.

The tone rule supports the test of whether feedback follows a wrong grade (`code/feedback-discordant/README.md`).
Each model wrote feedback on the board's 100 short answers twice: once told the teacher's grade m, and once told its
mirror, 5 − m, so that an answer the teacher gave 5 was said to have scored 0. The work is the same in both, so
feedback that responds only to the work has the same tone in both. The told-grade slope S is the change in tone per
point of told grade with the work held fixed, from the paired difference between the two versions of each answer's
feedback; a positive S means the tone follows the told grade. Beside it, W is the slope of tone on the teacher's grade
when no grade is told, which measures how far the same model's tone follows the quality of the work. The study's
planted-effect check, a shift of half a model's tone standard deviation across the scale, was detected in 86.5% of
400 simulated datasets, with the null flagged in 7.0%.

Every one of the 22 models reads TONE FOLLOWS THE TOLD GRADE, each significant after the Benjamini–Hochberg correction
across the 22. S runs from +0.215 [+0.062, +0.349] (Llama 3.2 3B) and +0.252 [+0.158, +0.343] (GPT-5 Mini) to +1.165
[+1.025, +1.310] (Gemma 3 27B) and +1.214 [+0.960, +1.468] (Olmo 3.1 32B), in tone points per point of told grade. For
20 of the 22, the lower end of the interval lies above the planted effect; the exceptions are GPT-5 Mini and Llama 3.2
3B. For eight models the point estimate of S is at least as large as W, so that, as far as point estimates show, a
wrong grade moves the tone at least as much as the quality of the work does; the ratio has no interval and was
registered as descriptive only, because W can be near 0: Qwen3 235B, Gemma 3 4B, Gemini 3.5 Flash Lite, Olmo 3.1 32B, GPT-OSS 20B, Gemma 3 27B and Ministral 8B
(S / W from 1.01 to 1.65), and Llama 3.2 3B (2.40), whose tone barely follows the work (W 0.090).

An earlier measure, the halo, told each model the true grade and compared its feedback with feedback written with no
grade: the correlation between tone and grade when the grade was shown minus the same correlation when it was hidden.
On that measure, whose intervals were not checked on simulated graders (Section 4.6), nine of the 22 models had a
halo interval that excluded 0, eight toward the told grade and one, GPT-5 Mini, away from it, and 13 did not (`code/feedback-board/out/feedback-board.json`). Told a wrong grade, every model's tone follows
it. This includes models whose halo was near 0, such as GLM 5.3 (halo +0.027 [−0.069, +0.147], S +1.039 [+0.870,
+1.221]); GPT-5 Mini, whose halo was negative (−0.166 [−0.319, −0.010]); and Qwen3 235B, whose halo estimate was
negative but not shown to differ from 0 (−0.095 [−0.261, +0.105]). When the told grade is the
true one, a model that copies it and a model that uses it as information about the work write similar feedback, so the
halo could not separate the two. The board therefore scores the feedback strand from S and W (Section 4.5), and no
longer from the halo.

The Withholding Answers evaluator judged that 59.3% (Gemma 3 27B) to 100% (Claude Opus 5.5 and GPT-6 Astra) of each
model's feedback on answers below full credit gives away the answer. The board's prompt asks feedback to name what was
missing and a next step, which in grading is often the purpose of feedback, so this share is shown and not ranked.

The generative fine-tune of Section 5.1 changed these behaviors as well. Its working effect fell by 0.325 points of 4
(95% interval 0.245 to 0.408; FINE-TUNED READS THE WORKING LESS), although it still reads the working by the board's
bar.
Its pushback effect (+7.2% for the base, +5.1% for the fine-tuned model, difference −2.1% [−6.0%, +1.9%]) and its
halo, the earlier feedback measure (+0.11 against +0.24, difference +0.13 [−0.07, +0.34]) are UNMEASURED, because their planted-effect checks
failed. Its replies parsed slightly more often (+0.31 percentage points [+0.12, +0.52]).

**Answer to RQ3.** Most models give way more to a student's bare objection than to a request for a second look: 17 of
22 raise their grade more after the objection, including six of the eight models without a flag (no note's mean gain above 5% of the scale, and no blank
answer credited). Nearly every model credits the working in a mathematics solution rather than only the
final answer, but the models that read the working differ by up to 1.865 points of 4 on what a slip at the end
costs. Told a grade that contradicts the work, every one of the 22 models writes feedback whose tone, measured by a
word rule validated on tutoring replies, follows that grade, and for eight of them the point estimate of that shift is
at least as large as the shift with the quality of the work (a descriptive ratio with no interval). Fine-tuning one model on essays made it read the mathematics working less.

### 5.4 Recordings and images (RQ4)

Models that accept sound, images or video were graded on tasks in those media, with probes that test whether the
grade comes from the recording. Each probe has a known sound response: a silent recording or a blank screen should
receive the lowest grade, and the same recording described as coming from a strong or a weak student should receive
the same grade.

Seven audio models graded the pronunciation of 100 English sentences read by Mandarin-speaking children and adults,
each scored by five experts from 0 to 10 (Zhang et al. 2021; `code/speech/README.md`). The experts' mean agreement
with each other is QWK 0.614. Table 5.4 gives the results.

*Table 5.4. Speech. QWK with the experts; share of the experts' agreement with its 95% interval over recordings; QWK
between two gradings of the same recording; the share of silent recordings and of plain-tone recordings given more
than the minimum; and the effect of describing the speaker as strong rather than weak, as a share of the scale, with
its 95% interval. Sources: `code/out/speech/` and `code/out/public/speech.json`.*

| model | QWK | share of the raters' agreement [95%] | retest QWK | silence credited, % | tone credited, % | strong vs weak label, % of scale [95%] |
|---|---|---|---|---|---|---|
| Gemini 3.8 Flash | 0.649 | 105.7% [97.3, 117.4] | 0.904 | 100.0 | 96.7 | +8.6 [+6.9, +10.4] |
| Perceptron mk1.5 | 0.587 | 95.7% [84.0, 108.3] | 0.972 | 96.7 | 6.7 | +22.1 [+18.4, +26.1] |
| Gemini 3.5 Flash Lite | 0.536 | 87.4% [74.3, 101.1] | 0.936 | 100.0 | 10.0 | +9.6 [+6.1, +13.2] |
| Gemini 4 Argon | 0.483 | 83.2% [63.0, 107.8] | 0.926 | 100.0 | 8.3 | +10.0 [+8.2, +11.9] |
| MiMo v2.6 Flash | 0.469 | 76.4% [64.1, 88.6] | 0.741 | 89.7 | 41.4 | +11.2 [+8.4, +13.9] |
| Voxtral Small 24B | 0.239 | 38.9% [25.2, 55.7] | 0.894 | 100.0 | 100.0 | +36.0 [+34.5, +37.5] |
| Muse Spark Open | 0.237 | 38.4% [21.8, 57.0] | 0.412 | 5.0 | 0.0 | −0.3 [−6.7, +6.2] |

Six of the seven models credit 89.7% to 100% of silent recordings. Gemini 3.8 Flash, with the highest point estimate (105.7% of the
experts' agreement, an interval that overlaps Perceptron mk1.5's), credits every silent recording and 96.7% of plain tones; Gemini 3.5 Flash Lite credits every
silent recording while reaching 87.4%. The seventh model, Muse Spark Open, credits 5.0% of silent recordings, but it
reaches only 38.4% of the experts' agreement and grades the same recording twice at a QWK of only 0.412.
Describing the speaker as strong raised the grade for six of the seven models, by +8.6% to +36.0% of the scale.

A second study tested whether an audio model recognizes a correct spoken answer as well in a less common language
(`code/language/README.md`). It used the same sentences read aloud in 18 languages (Conneau et al. 2023), six each
of high, middle and low resource. Each recording was paired once with its own sentence and once with another as an
English model answer. Six of the seven models are WORSE ON LOW-RESOURCE LANGUAGES, with accuracy on the high tier
minus accuracy on the low tier from +0.04 (Gemini 3.8 Flash, [+0.02, +0.07]; Gemini 4 Argon, [+0.01, +0.06]) to +0.38
[+0.34, +0.41] (Perceptron mk1.5); Gemini 3.5 Flash Lite's gap is +0.14 [+0.10, +0.18]. Muse Spark Open shows NO GAP
DETECTED (+0.01 [−0.02, +0.05]; a gap up to 0.05 is not ruled out). The run for Voxtral Small 24B is incomplete: 110 of
its 1,080 gradings failed. Of 116 gradings that failed at first, an earlier re-send recovered 4; the 112 that remained were all transport
errors and were sent once more (CHANGE 3 in
`code/language/study.py`); 2 succeeded and 110 met the provider's rate limit again. Gemini 4 Argon's 84 failed
gradings are replies with no readable mark, which the harness counts as failures and does not ask again.

Fifteen models graded 122 handwritten solutions to Russian school-leaving mathematics problems, each with one
official expert score, on three scales (0 to 2, 0 to 3 and 0 to 4; Khrulev 2025; `code/images/README.md`). With one
score per solution there is no ceiling, so these are agreement figures without a reference. Claude Opus 5.5 reaches
QWK 0.685 to 0.754 across the three scales, GPT-6 Astra 0.644 to 0.735, and Claude Fable 5.1 0.511 to 0.851, the
highest on the 0 to 4 scale. The note probes were drawn onto the page, in a white band under the student's work.
Twelve of the 15 models are raised by such a note on at least one scale, with an interval above 0, by up to 43.0% of
the scale (Ministral 8B on the 0 to 2 scale). Claude Haiku 5.5, whose largest gain from a text note is 2.0% [0.2%, 4.0%] of the
scale, is raised by 15.2% [8.1%, 23.2%] and 10.9% [6.2%, 16.4%] on the 0 to 3 and 0 to 4 scales. Only Claude Opus
5.5, GPT-6 Astra and Claude Fable 5.1 are not shown to be raised on any scale (`code/out/images/`).

Video was tested on 100 recordings of laparoscopic training tasks, each rated by three raters on a total scale of 4
to 20 (Funke et al. 2026; `code/video/README.md`). A recording's length predicts its rating, and the prompt states
the length, as the raters knew it; a simulated grader that only times the recording reaches QWK 0.57, the raters'
own agreement. The pre-registered measure is therefore agreement beyond length: the partial Spearman correlation of
the model's grade with the raters' mean, controlling for length within each task. A model WATCHES THE RECORDING if
this interval lies above 0. Models without video input were sent 16 evenly spaced frames. Table 5.5 gives every run.

*Table 5.5. Video. Agreement beyond length with its 95% interval over recordings; QWK with the raters' mean; the share
of black-screen and frozen-frame recordings (30 each) given more than the minimum; and the pre-registered verdict.
Source: `code/out/public/video.json`.*

| model | input | agreement beyond length [95%] | QWK | black screen credited, % | frozen frame credited, % | verdict |
|---|---|---|---|---|---|---|
| Gemini 4 Argon | video | +0.459 [+0.212, +0.634] | 0.532 | 53.3 | 3.3 | WATCHES THE RECORDING |
| Gemini 3.8 Flash | video | +0.330 [+0.062, +0.540] | 0.293 | 100.0 | 100.0 | WATCHES THE RECORDING |
| Gemini 3.8 Flash | 16 frames | +0.254 [+0.038, +0.445] | 0.130 | 100.0 | 100.0 | WATCHES THE RECORDING |
| GLM 5.3 Flash | video | +0.251 [+0.021, +0.453] | 0.154 | 3.3 | 56.7 | WATCHES THE RECORDING |
| GPT-6 Astra | 16 frames | +0.211 [−0.032, +0.431] | 0.228 | 0.0 | 23.3 | ADDS NOTHING TO THE STOPWATCH |
| GPT-5 Mini | 16 frames | +0.137 [−0.102, +0.384] | −0.033 | 0.0 | 70.0 | ADDS NOTHING TO THE STOPWATCH |
| DeepSeek V4.1 Flash (Oct 17 snapshot) | 16 frames | +0.136 [−0.104, +0.374] | 0.005 | 16.7 | 36.7 | ADDS NOTHING TO THE STOPWATCH |
| DeepSeek V4.1 Flash | 16 frames | +0.135 [−0.058, +0.306] | −0.035 | 0.0 | 23.3 | ADDS NOTHING TO THE STOPWATCH |
| Gemma 4 26B A4B | video | +0.123 [−0.068, +0.314] | 0.003 | 96.7 | 26.7 | ADDS NOTHING TO THE STOPWATCH |
| Gemini 3.5 Flash Lite | video | +0.094 [−0.123, +0.307] | 0.011 | 80.0 | 53.3 | ADDS NOTHING TO THE STOPWATCH |
| Claude Opus 5.5 | 16 frames | +0.084 [−0.123, +0.286] | 0.215 | 0.0 | 13.3 | ADDS NOTHING TO THE STOPWATCH |
| Perceptron mk1.5 | video | +0.083 [−0.140, +0.302] | −0.008 | 0.0 | 0.0 | ADDS NOTHING TO THE STOPWATCH |
| Gemma 4 31B | video | +0.072 [−0.125, +0.256] | −0.011 | 0.0 | 0.0 | ADDS NOTHING TO THE STOPWATCH |
| Claude Fable 5.1 | 16 frames | +0.068 [−0.169, +0.305] | 0.186 | 0.0 | 16.7 | ADDS NOTHING TO THE STOPWATCH |
| Claude Haiku 5.5 | 16 frames | +0.036 [−0.171, +0.228] | 0.039 | 3.3 | 70.0 | ADDS NOTHING TO THE STOPWATCH |
| Gemma 3 27B | 16 frames | −0.010 [−0.204, +0.187] | 0.029 | 30.0 | 46.7 | ADDS NOTHING TO THE STOPWATCH |
| GPT-5.6 Luna | 16 frames | −0.043 [−0.271, +0.186] | 0.006 | 0.0 | 13.3 | ADDS NOTHING TO THE STOPWATCH |
| MiMo v2.6 Flash | video | −0.045 [−0.245, +0.174] | 0.125 | 96.7 | 90.0 | ADDS NOTHING TO THE STOPWATCH |
| Qwen3.8 27B | video | −0.091 [−0.303, +0.162] | 0.130 | 0.0 | 26.7 | ADDS NOTHING TO THE STOPWATCH |
| Gemma 3 4B | 16 frames | −0.103 [−0.318, +0.108] | −0.019 | 100.0 | 100.0 | ADDS NOTHING TO THE STOPWATCH |
| Nova 2 Lite | video | — | — | 23.3 | 0.0 | DID NOT RATE |
| Raters (one against the others) | video | +0.575 | 0.571 | — | — | reference |

Four of the 21 runs WATCH THE RECORDING: Gemini 4 Argon (+0.459, four-fifths of the raters' +0.575), Gemini 3.8
Flash from video and from frames, and GLM 5.3 Flash. Sixteen read ADDS NOTHING TO THE STOPWATCH. That verdict means only that the interval reaches 0; the upper ends, from +0.108 to +0.431, leave room for
agreement beyond length of up to three-quarters of the raters'. Nova 2 Lite described the video instead of rating it
on nearly every grading. Nine of the 21 runs never credited a black screen; Gemini 3.8 Flash and Gemma 3 4B credited
every black screen and every frozen frame. The two Gemma 4 endpoints were charged about 2,860 and 2,880 input tokens
per recording whatever its length, so they were most likely sent a few frames rather than the recording, as MiMo v2.6
Flash was (2,508).

A further video study asked whether a longer recording hides an error (`code/video/LENGTH.md`). Each of 205
recordings was asked whether its labeled error happened, once as recorded and once joined to three recordings of the
same task in which the error did not happen, so four times as long. Five runs read LENGTH HURTS DETECTION, a fall in
balanced accuracy: GPT-5 Mini (−0.135 [−0.221, −0.044]), Claude Opus 5.5 (−0.127 [−0.200, −0.052]), GPT-6 Astra
(−0.111 [−0.187, −0.033]), Claude Haiku 5.5 (−0.101 [−0.180, −0.023]) and Claude Fable 5.1 (−0.091 [−0.177, −0.002])
(`code/out/public/video_length.json`). All five saw 16
frames, and 16 frames from a recording four times as long are four times as sparse, so these runs show what a
frames-only grader does with a long recording rather than the effect of length alone; this caveat was registered
before those runs. The other 13 runs read NO DETECTABLE EFFECT, with losses of 0.02 to 0.14 not ruled out.

The last study audited whether a video model says it cannot see a speaker who is plainly on screen, by skin tone and
lighting (`code/perception/README.md`). It used 1,280 recordings of consenting adults answering a question to
camera (Porgali et al. 2023), with skin tone taken only from the dataset's Monk labels, and lighting from the
dataset's label for whether a recording was made in daylight or after dark. The license does not allow sending a
reduced copy of a video, and the hosted endpoints refused most full-length videos as too large (a 102 MB and a 168 MB
video were refused in a pilot; the sample's median is about 155 MB), so hosted models are not in this study. Three
open models were run on the study's own GPU: Gemma 4 26B A4B, Gemma 4 31B and Qwen3.8 27B. All three graded 1,278 of
the 1,280 recordings, and all three said "not visible" on each of 10 black, silent control clips. Gemma 4 26B A4B and
Gemma 4 31B said they could not see the speaker in 0 of 1,278 recordings and refused none. With no failures, there is
no gap between groups to measure, so the pre-registered gap verdicts read UNMEASURED. Zero failures in 1,278 puts the
failure rate below 0.23% (one-sided 95% upper bound, 1 − 0.05^(1/n)). By tone group the bound is below 0.7% for Monk
3 to 4, below 1.7% to 1.8% for Monk 6 and Monk 7 to 8, and below 7.2% for Monk 9 to 10, the darkest group, where the
corpus holds only 40 eligible recordings. Qwen3.8 27B DID NOT DO THE TASK: 21% of its replies had no usable answer,
above the registered limit of 20%, and its 822 "cannot see" replies are not credible, because in 372 of them it also
rated the speaker's delivery. Before the study moved to its own GPU, one hosted model, MiMo v2.6 Flash, was sent the
10 control clips in a pilot. On 7 of them it said a speaker was visible and audible and rated the delivery 3 to 5.
This is a pilot observation, not a result.

**Answer to RQ4.** Most models that grade recordings do not reliably notice when there is nothing to grade: six of
seven audio models credit nearly every silent recording, and 12 of 21 video runs credit a black screen at least
once. Only four of 21
video runs are shown to grade the recording beyond its length. A note written onto a handwritten page raises the
grade for 12 of 15 models, including Claude Haiku 5.5, whose largest gain from a text note is 2.0% [0.2%, 4.0%] of the scale. Six of seven audio
models, one of them on an incomplete run, recognize a correct spoken answer less well in low-resource languages. Two open video models said they could see every one of 1,278
speakers, which bounds their failure rate below 0.23% overall but below only 7.2% for the darkest skin-tone group;
hosted video models could not be tested under the corpus's license.

### 5.5 Fairness and stability (RQ5)

Fairness was measured as a difference between groups at the same human grade. A gap is reported beyond the gap that a
second human rater shows wherever the corpus releases two raters, because a noisy second reader can show a gap by
regression toward each group's own mean even when grading fairly. The ELLIPSE corpus of English learners' essays
releases both raters' grades (Crossley et al. 2023; `code/fairness-ellipse/README.md`). Essays were matched exactly on
rater 1's grade, from 1 to 5, and the statistic D is the model's gap minus rater 2's gap on the same essays. A
negative D means the model grades group A lower. Three contrasts were pre-registered: economically disadvantaged
against not (C1, the primary contrast, 1,000 essays per group), Black or African American against White (C2, 465 per
group) and Hispanic or Latino against White (C3, 469 per group). Table 5.6 gives every model's figures.

*Table 5.6. Fairness. D for each ELLIPSE contrast, and for the replication's primary arm RA, on the 1 to 5 scale; and
the disability gap on ASAP 2.0, on the 1 to 6 scale. Each with its 95% bootstrap interval over essays. Negative
values mean the model grades the first-named group lower. Sources: `code/fairness-ellipse/out/result.json`,
`code/fairness-ellipse/out/rep-result.json` and `code/disability/out/result.json`.*

| model | C1 economic, D [95%] | C2 Black vs White, D [95%] | C3 Hispanic vs White, D [95%] | replication RA, D [95%] | disability gap [95%] | disability verdict |
|---|---|---|---|---|---|---|
| Claude Opus 5.5 | −0.008 [−0.058, +0.040] | −0.067 [−0.138, +0.008] | −0.136 [−0.207, −0.066] | −0.084 [−0.146, −0.025] | −0.219 [−0.265, −0.173] | GAP REPLICATES |
| Claude Fable 5.1 | +0.014 [−0.037, +0.068] | −0.104 [−0.183, −0.025] | −0.164 [−0.239, −0.086] | −0.129 [−0.191, −0.065] | −0.247 [−0.298, −0.196] | GAP REPLICATES |
| GPT-6 Astra | +0.024 [−0.027, +0.077] | −0.015 [−0.088, +0.062] | −0.083 [−0.164, −0.004] | −0.011 [−0.074, +0.050] | −0.217 [−0.268, −0.162] | GAP REPLICATES |
| Claude Haiku 5.5 | −0.005 [−0.061, +0.051] | −0.049 [−0.133, +0.037] | −0.108 [−0.190, −0.029] | −0.043 [−0.113, +0.025] | −0.166 [−0.210, −0.123] | GAP REPLICATES |
| GLM 5.3 Flash | +0.049 [−0.006, +0.107] | −0.077 [−0.160, +0.003] | −0.110 [−0.192, −0.026] | −0.040 [−0.106, +0.024] | −0.393 [−0.451, −0.334] | GAP REPLICATES |
| GPT-5 Mini | +0.005 [−0.055, +0.063] | −0.060 [−0.146, +0.026] | −0.109 [−0.196, −0.023] | −0.040 [−0.112, +0.032] | −0.172 [−0.223, −0.120] | GAP REPLICATES |
| DeepSeek V4.1 Flash (Oct 17 snapshot) | +0.028 [−0.029, +0.084] | −0.110 [−0.189, −0.030] | −0.122 [−0.205, −0.041] | −0.100 [−0.167, −0.033] | −0.270 [−0.330, −0.211] | GAP REPLICATES |
| DeepSeek V4.1 Flash | +0.041 [−0.015, +0.097] | −0.112 [−0.191, −0.030] | −0.115 [−0.196, −0.034] | −0.055 [−0.120, +0.012] | −0.333 [−0.397, −0.268] | GAP REPLICATES |
| GLM 5.3 | −0.033 [−0.090, +0.024] | −0.052 [−0.131, +0.028] | −0.094 [−0.173, −0.013] | −0.049 [−0.118, +0.018] | −0.367 [−0.422, −0.310] | GAP REPLICATES |
| Gemma 4 31B | +0.008 [−0.045, +0.061] | −0.062 [−0.140, +0.015] | −0.136 [−0.213, −0.060] | −0.067 [−0.131, −0.001] | −0.235 [−0.291, −0.178] | GAP REPLICATES |
| Gemini 3.5 Flash Lite | −0.002 [−0.058, +0.052] | −0.078 [−0.164, +0.006] | −0.150 [−0.231, −0.066] | −0.085 [−0.154, −0.016] | −0.429 [−0.506, −0.349] | GAP REPLICATES |
| GPT-5.6 Luna | −0.007 [−0.065, +0.052] | −0.071 [−0.155, +0.011] | −0.072 [−0.156, +0.009] | −0.060 [−0.129, +0.010] | −0.202 [−0.260, −0.143] | GAP REPLICATES |
| Gemma 4 26B A4B | −0.016 [−0.069, +0.037] | −0.047 [−0.125, +0.032] | −0.115 [−0.198, −0.036] | −0.041 [−0.109, +0.027] | −0.347 [−0.410, −0.283] | GAP REPLICATES |
| Phi-4 | −0.042 [−0.106, +0.024] | −0.060 [−0.155, +0.032] | −0.062 [−0.158, +0.032] | −0.035 [−0.118, +0.050] | −0.279 [−0.340, −0.217] | GAP REPLICATES |
| Qwen3 235B | −0.020 [−0.075, +0.036] | −0.067 [−0.146, +0.015] | −0.126 [−0.207, −0.045] | −0.054 [−0.123, +0.014] | −0.212 [−0.276, −0.148] | GAP REPLICATES |
| Gemma 3 27B | −0.021 [−0.079, +0.039] | −0.056 [−0.140, +0.030] | −0.117 [−0.205, −0.032] | −0.062 [−0.129, +0.005] | −0.247 [−0.301, −0.192] | GAP REPLICATES |
| Ministral 8B | −0.036 [−0.092, +0.021] | −0.062 [−0.146, +0.026] | −0.124 [−0.207, −0.041] | −0.056 [−0.126, +0.012] | −0.124 [−0.167, −0.082] | NO GAP OF 0.2 OR MORE |
| GPT-OSS 20B | +0.001 [−0.065, +0.065] | −0.060 [−0.153, +0.034] | −0.047 [−0.144, +0.051] | −0.011 [−0.092, +0.069] | −0.232 [−0.285, −0.177] | GAP REPLICATES |
| DeepSeek V4 Pro | +0.032 [−0.028, +0.094] | −0.088 [−0.178, +0.006] | −0.117 [−0.209, −0.026] | −0.103 [−0.181, −0.026] | −0.275 [−0.336, −0.211] | GAP REPLICATES |
| Olmo 3.1 32B | −0.039 [−0.095, +0.020] | −0.103 [−0.185, −0.022] | −0.096 [−0.179, −0.013] | −0.055 [−0.126, +0.014] | −0.247 [−0.297, −0.197] | GAP REPLICATES |
| Gemma 3 4B | −0.025 [−0.085, +0.034] | −0.064 [−0.149, +0.025] | −0.119 [−0.203, −0.030] | −0.060 [−0.128, +0.015] | −0.086 [−0.141, −0.029] | NO GAP OF 0.2 OR MORE |
| Llama 3.2 3B | −0.072 [−0.145, −0.001] | −0.024 [−0.129, +0.082] | −0.030 [−0.132, +0.072] | −0.027 [−0.112, +0.058] | −0.213 [−0.288, −0.140] | GAP REPLICATES |

On economic status (C1), every one of the 22 models reads NO MORE THAN A SECOND HUMAN; Llama 3.2 3B's interval just
excludes 0 (−0.072 [−0.145, −0.001]) and lies within the pre-registered band. On Black against White (C2), four
models have an interval below 0 (Claude Fable 5.1, Olmo 3.1 32B, and DeepSeek V4.1 Flash and its October 17 snapshot,
−0.103 to −0.112); none lies wholly below the pre-registered −0.10, so these four are among the ten that read
INCONCLUSIVE, and 12 read NO MORE THAN A SECOND HUMAN. On Hispanic against White (C3), 18 of the 22 models have an interval below 0, with estimates from
−0.083 (GPT-6 Astra) to −0.164 (Claude Fable 5.1). None lies wholly below the pre-registered −0.10, so 20 models read
INCONCLUSIVE and two NO MORE THAN A SECOND HUMAN. Rater 2's own gap on these essays is +0.066 [−0.023, +0.160].

The Hispanic against White signal was then tested in a pre-registered replication on 1,407 Hispanic learners' essays
not used before, set against the same 469 White essays, because the corpus holds no more White essays. The
pre-registered verdict, which rests on the four graders named in advance (Claude Haiku 5.5, Gemini 3.5 Flash Lite,
GPT-5 Mini and Qwen3 235B), is MIXED: Gemini 3.5 Flash Lite keeps an interval below 0 (−0.085 [−0.154, −0.016]) and
the other three do not. Across all 22 models, six keep an interval below 0 in the primary arm (RA): Claude Fable 5.1,
Claude Opus 5.5, DeepSeek V4 Pro, DeepSeek V4.1 Flash's October 17 snapshot, Gemini 3.5 Flash Lite and Gemma 4 31B.
In a second arm with the two raters' roles swapped (RB), rater 2's own gap is −0.097 [−0.177, −0.020], and one model,
Claude Fable 5.1, keeps an interval below 0 (−0.061 [−0.122, −0.003]). Because the White essays are shared by the
first draw and the replication, a property of those 469 essays cannot be separated from a property of the models.

A second fairness study used ASAP 2.0 essays by students identified with a disability and by students not identified,
3,000 essays matched exactly on the human grade (`code/disability/README.md`). ASAP 2.0 releases only the adjudicated
grade, so the gap is measured against that grade, not beyond a second rater. Every one of the 22 models grades the
identified group lower, with an interval below 0, from −0.086 (Gemma 3 4B) to −0.429 (Gemini 3.5 Flash Lite) on the 1
to 6 scale. Twenty read GAP REPLICATES, and Gemma 3 4B and Ministral 8B read NO GAP OF 0.2 OR MORE. The pre-registered
reading for a gap that the comparison models share is SHARED GAP: the design cannot separate a bias shared by the human
panel from one shared by the models, because the two raters' separate grades before adjudication are not released.

A follow-up reanalysis asked what carries this gap (`code/disability-mechanism/README.md`). Its first part, a reverse
regression (Conway and Roberts 1983) that asks whether the identified group receives higher human grades at the same machine grade, could not
be measured: in simulations shaped like this corpus, a model bias of 0.30 or 0.50 points was detected in none of 200
datasets, because measurement error alone pushes the statistic far below 0. Every model therefore reads UNMEASURED on
that part, and whether the gap reflects the models or the error in the human grades remains open. The second part
measured two surface features of each essay by fixed rules: its length, and its convention errors per 100 words
(misspellings by the pyspellchecker 0.8.1 dictionary (Barrus 2024), excluding words from the assignment's own prompt and sources,
together with a lowercase "i" and sentences that begin in lowercase). These are rule-coded proxies, not validated
measures of writing conventions. At the same human grade, the identified group's essays carry 0.95 more convention
errors per 100 words and are 7.7 words shorter, and every model gives a lower grade for more convention errors at the
same human grade. For all 20 models with a gap, the verdict is SURFACE FEATURES ACCOUNT FOR PART OF THE GAP: the two
features account for 9% (GLM 5.3) to 32% (Llama 3.2 3B) of the gap, and at equal length and convention errors the gap
remains between −0.144 (Llama 3.2 3B) and −0.373 (Gemini 3.5 Flash Lite), every interval below 0. The planted-effect
check of this part, a gap carried entirely by convention errors, was detected in 90.5% of simulations.

Stability was measured by grading the same 100 short answers with older and newer releases of the same model family
(`code/out/lineage-2026-10-23/drift.txt`). Two measures were compared: the mean shift in grades on the 0 to 5 scale,
and the QWK between the two releases set beside the QWK of the older release with itself when asked twice. Of seven
comparisons, four show a mean shift: GPT-4o-mini to GPT-4.1-mini +0.24 [+0.09, +0.40], GPT-4.1-mini to GPT-5 Mini
+0.34 [+0.14, +0.55], GPT-4o-mini to GPT-5.6 Luna +0.49 [+0.29, +0.70] and Claude Haiku 4.5 to Claude Haiku 5.5 −0.49
[−0.66, −0.33]. In three, no shift was shown: GPT-5 Mini to GPT-5.6 Luna (−0.09 [−0.24, +0.04]), Qwen 2.5 72B to Qwen3 235B
(−0.04 [−0.19, +0.09]) and DeepSeek V3 to DeepSeek V4.1 Flash (+0.13 [−0.06, +0.35]), whose interval allows a shift as
large as those shown. In all seven, the two releases
agree with each other less than the older release agrees with itself: QWK across releases runs from 0.728 to 0.895,
and within one release from 0.901 to 0.983. For Claude Haiku 4.5 to 5.5 the figures are 0.802 across and 0.983
within.

**Answer to RQ5.** On economic status, every model's gap lies within the pre-registered band of 0.15 points of a
second human rater's, though Llama 3.2 3B's is shown to be lower. On Black against White learners, four models grade
Black learners lower beyond a second rater, none by an interval wholly below the pre-registered −0.10, and ten read
INCONCLUSIVE. On Hispanic against White learners, 18 of 22 models grade Hispanic learners lower beyond a second rater
in the first draw, but no model's interval lies wholly below the pre-registered −0.10 and the pre-registered
replication is MIXED, so this is not established as a model bias. Every model grades essays by students identified with a disability lower than essays by other
students with the same adjudicated grade, a gap the design cannot attribute to the models rather than to the human
panel. Convention errors and length, measured by rule, account for at most a fifth of that gap for 17 of the 20 models
with a gap, and most of it remains at equal length and errors. In exploratory
comparisons, newer releases of a model family change individual grades more than the older release changes when
asked twice (point estimates), and in four of seven comparisons they shift the mean grade, in both directions.

### 5.6 Cost to the environment (RQ6)

The energy of a grading was measured where the model could be run on the study's own hardware, and estimated where
it could not (`code/energy/README.md`). Nine open models were served on one NVIDIA A100 80GB GPU and given the board's
100 cases per task, 16 requests at a time. The GPU's energy counter and the count of finished gradings were read every
second. NET energy is the GPU's energy above idle per grading; FULL-STACK multiplies it by 1.72, from a published split
of a hosted prompt's energy in which the accelerators are 58% of the total. That factor is an assumption, not a
measurement of this machine. The comparison is the published per-token estimate (Jegham et al. 2025, as implemented
in `code/docs/ENERGY.md`), evaluated at each model's own measured token counts for a small model (Llama 3.1 8B) and a
mid-size one (GPT-4o).

All 27 model-task figures read BELOW THE SMALL-MODEL ESTIMATE (`code/out/public/energy_measured.json`). NET energy per
grading runs from 0.845 mWh (Llama 3.2 3B, short answers) to 25.529 mWh (Phi-4, code); FULL-STACK from 1.456 to 44.016
mWh. The small-model estimate exceeds the FULL-STACK measurement by a factor of 1.35 to 17.3, with a median of 3.97, and
the mid-size estimate exceeds it by a factor of 15.2 to 128 (computed from the file's values). Sending the same
requests one at a time instead of 16 at a time used 4.9 to 15.0 times the energy per grading (measured on short
answers and essays, 18 of the 27 figures). For hosted models,
which cannot be measured this way, the published method gives, for a mid-size model, 0.187 Wh per short-answer
grading, 0.464 Wh per essay, 0.534 Wh per program, 3.873 Wh per program graded by a reasoning-heavy model and 16.393
Wh per 30-minute video (`code/out/public/energy_tasks.json`).

Running the model is only part of a grading's footprint, so a lifecycle estimate adds a share of training, the making
of the hardware and buildings, and the water used to generate the electricity (`code/docs/LIFECYCLE.md`). Because no
company publishes how many queries a model serves, training's share is given as a low, central and high case. In the
central case, a short-answer grading uses 0.316 Wh, 0.131 g of carbon dioxide equivalent (CO2e) and 1.28 mL of water;
an essay 0.783 Wh, 0.324 g and 3.18 mL; a program 0.902 Wh, 0.373 g and 3.66 mL; and a 30-minute video 27.664 Wh,
11.453 g and 112.38 mL (`code/out/public/lifecycle_tasks.json`). With everything added, a short-answer grading's energy
is 1.1 to 2.7 times its running energy from the low to the high case (0.206 and 0.505 Wh against 0.187 Wh; computed
from the file's values).

The lifecycle figures were set beside everyday activities measured on comparable boundaries, using the sources listed
with each comparison (`code/out/public/lifecycle_compare.json`). A teacher's term of short answers, 150 students
times 10 assignments or 1,500 gradings, comes to 196 g CO2e, 473.5 Wh and 1,923 mL of water in the central case.
Driving 1 km in an average European gasoline car emits 245 g CO2e over its life cycle, the equivalent of 1,875
short-answer gradings, and in a battery electric car 80 g, or 612 gradings (Bieker 2021, for the International Council on Clean Transportation). Streaming video for one hour
in Europe uses electricity that emits 55 g, or 421 gradings (Carbon Trust 2021). A quarter-pound beef patty emits
11,240 g over its life cycle, or 86,016 gradings (Poore and Nemecek 2018).

**Answer to RQ6.** On one modern GPU in a batch, an open model of up to 32 billion parameters used 0.845 to 25.529 mWh
per grading at the GPU, below the published estimate for a small model in all 27 measurements, and sending requests
one at a time multiplied that by 4.9 to 15.0 on short answers and essays. For hosted models, which could not be measured, the published method
gives 0.187 to 0.534 Wh per written grading for a mid-size model, and the central lifecycle estimate is 0.316 to 0.902
Wh, 0.131 to 0.373 g CO2e and 1.28 to 3.66 mL of water per written grading. A teacher's term of 1,500 short-answer
gradings comes to about the carbon of driving 1 km in a gasoline car (196 g against 245 g).

## 6. Discussion

The results separate two properties that an agreement figure runs together: how often a model agrees with expert
raters on ordinary work, and what it does with work designed to move it. Robustness on one kind of probe did not carry
over to the others: six of the eight models without a flag (no note's mean gain above 5% of the scale, and no blank answer credited)
still raised their grade more after a bare objection than after a request to double-check, and every model wrote
feedback whose tone, as a word rule validated on tutoring replies measures it, followed a wrong grade it was told. A grader's agreement is
therefore evidence about one of its properties, as the standard framework for automated scoring already holds
(Williamson, Xi and Breyer 2012), and the failures measured here are not visible in it.

The probes that move a grade are, in the terms of the security literature, indirect prompt injection (Greshake et al.
2023): the student's answer is the channel through which an instruction reaches the grader. The benchmark adds to the
studies that found this for language-model graders (Li et al. 2026; Raina, Liusie and Gales 2024; Hwang et al. 2025;
Sahoo et al. 2026) a common plain prompt, many vendors on three tasks under one protocol and the effect of the
grader's settings, and it found no setting that helps every model. High
reasoning effort, where a model offers it, reduced gaming for most of the models that have the setting, in line with
the gain in robustness from inference-time reasoning reported for other attacks (Zaremba et al. 2025). The one guard
sentence tested fixed some models and made others more gameable, which matches the finding that no defense dominates
across judges (Li, Xu, et al. 2025) and that a defensive prompt can raise attack success for some models (Chen, Hu, et
al. 2025). The conclusion is about this sentence, not about prompt defenses in general:
marking the student's text as untrusted data is a stronger member of the family (Hines et al. 2024) and was not
tested. The hosting comparison and the controlled precision study read together say that the host serving an open
model was associated with how gameable it was, while 4-bit weights as such were not shown to be the cause for the two smaller dense models tested; the hosts
differ in more than precision (Hong et al. 2024; Gao, Liang and Guestrin 2025).

The pushback result fits the sycophancy literature (Sharma et al. 2023; Laban et al. 2023) and the finding that models
give way more to a casual follow-up turn than to an argument set out beside the original position (Kim and Khashabi
2025), which is how the objection was posed here. Because the comparison condition, a request for a second look, is
itself a prompt to reconsider, which lowered grades for ten of the 17 models that yield, the pushback effect is not
the objection's raw effect: it can exceed or fall short of it. The feedback result goes
further than the score-blind comparison that found a feedback halo first (Bulut et al. 2026). When the grade a model
is told is the true one, a model that copies it and a model that uses it as information about the work write similar
feedback, and the earlier measure could not tell them apart. Telling the model a grade that contradicts the work
separates the two, in the way assigned prior scores have been used to show anchoring in a language-model judge's
ratings (Kapetanovic et al. 2026), and under that test every model's feedback followed the told grade. The tone of feedback written beside a grade, as a
praise-and-criticism word rule measures it, therefore follows that grade even when the grade contradicts the work, at
least when the grade is badly wrong; whether the content of the feedback follows it was not measured.

On essays, scorers trained on tens of thousands of graded essays have a higher point estimate than every prompted
model, which replicates Ormerod and Kehat (2025). On short answers and code, where the corpora offer 1,627 and 29
graded answers, the trained scorers fall well behind, and every one of them gives credit to blank answers. The trained
scorers lead only on the corpus with tens of thousands of graded answers, and a fine-tuned language model was not shown to
differ from them there; with three corpora that differ in task as well as in training size, the benchmark cannot separate the two (on
how a trained scorer depends on its training set, see Heilman and Madnani 2015; a fine-tuned generative model can
match or beat a fine-tuned encoder, Latif and Zhai 2024). Fine-tuning a
language model on essays brought its essay agreement close to the trained scorers', with DeBERTa still ahead, although
the size of its own gain could not be confirmed by its check, but it agreed less on short answers, was gamed more on them and read mathematics working less. Narrow fine-tuning is known to
degrade behavior on tasks a model was not trained on (Qi et al. 2023; Luo et al. 2023), and the result is consistent with this for
short answers and mathematics working, in one model.

The recordings show the no-input problem documented for multimodal benchmarks (Chen et al. 2024; Foo et al. 2026) with
consequences for a student: most audio models gave credit to silent recordings, and few video runs added anything
measurable to what the recording's length predicts. Length carries real information about surgical skill for human
raters (Kelly et al. 2020), so a video run that adds nothing beyond length is not shown to ignore the video; it is not
shown to use it either. In the perception audit two open video models never said that a visible speaker could not be
seen, and the third did not do the task; with no failures there was no gap between groups to measure, and the bound
for the darkest skin-tone group is wide because the corpus holds few eligible recordings.

The disability comparison found a gap that every model shares. When the reference is a single human grade that carries
error and two groups differ in their average grade, models compared at the same human grade show a gap even if they
grade fairly, by regression toward each group's mean, and how an automated score is estimated can itself produce such
bias (Johnson, Liu and McCaffrey 2022). The design cannot separate the two, because ASAP 2.0 releases only the
adjudicated grade, and the reverse regression meant to address this could not detect a planted bias on this corpus.
Part of the gap goes with essays' convention errors and length, the surface features on which a feature-based engine
earlier showed no gap for students with learning disabilities (Buzick et al. 2016) and on which prompted models are
known to be harsh (Kucia, Chakraborty and Wróblewska 2026). On ELLIPSE, where a second rater's grades are released,
every model graded economically disadvantaged learners no more differently than a second rater did, within the
pre-registered band of 0.15 points; four models graded Black learners lower beyond a second rater, though none by an
interval wholly below the pre-registered threshold; and the Hispanic-against-White signal of the first draw read MIXED
in the pre-registered replication. In an exploratory comparison read from point estimates, newer releases changed
individual grades more than a model changes them when asked twice, a measure that differs from the
agreement-against-severity contrast of Sunkavalli (2026); in both, a version change is a change to the grader.

The energy of a grading was small on the measures used here, but the measured figures describe a GPU serving 16 requests at a time
and are a lower bound for a deployed grader (Elsworth et al. 2025; Fernandez et al. 2025), and cheaper grading can lead to
more grading (Luccioni, Strubell and Crawford 2025).

### Implications for practice

A school, a district or a vendor evaluating a language-model grader should ask for more than its agreement with human
raters. The grader should be tested with work whose correct grade is known in advance: a blank answer, an answer with
a request or a forged instruction added, the same work described as coming from a strong and from a weak student, and
a student who objects to the grade without a reason (RQ1, RQ2, RQ3). Agreement should be read beside the raters' own
agreement on the same task, and on essays beside a scorer that uses length alone (RQ1).

The grader that is tested should be the grader that is deployed. The prompt, the reasoning setting and the provider
that serves the model each changed how a model failed, and a change to any of them, or a new release of the model,
calls for the tests to be run again (RQ2, RQ5). A rule that gives the lowest grade to blank answers, applied before
any model sees them, would remove credit for blank answers whatever the model, though not for meaningless ones (RQ2).

Feedback should not be written from a grade that may be wrong, because its tone follows the grade it is given. Where feedback is generated beside a grade, the grade
should be checked first, or the feedback should be written without it (RQ3). A model that grades recordings should be
shown to notice when there is nothing to grade before it is used (RQ4).

A model fine-tuned for one kind of work should be tested on every kind of work it will grade, because fine-tuning one
model on essays lowered its agreement on short answers and its reading of mathematics working, while its agreement on
code moved up by an amount the study could not confirm (RQ1, RQ2, RQ3). Checking a grader for fairness needs two independent human grades
of the same work, or a gap the human reference shares cannot be told from one the model adds (RQ5).

### Implications for research

Evaluations of language-model graders should report agreement as a share of the raters' own agreement on the same
items, the signed direction in which the model departs from the raters, and the result of probes with a known correct
response. Every statistic should be checked on simulated data with a planted effect before it is read, as is standard for
evaluating statistical methods (Morris, White and Crowther 2019), because several measures here could not detect an
effect of the size that mattered and are reported as unmeasured.

Corpus builders can make fairness questions answerable by releasing each rater's grade before adjudication, and by
releasing grades for the same items from more than two raters. A private held-out set would answer whether the results
depend on items a model saw in training.

The wrong-grade test separates a feedback writer that copies a grade from one that uses it, and can be applied to
other feedback measures once they are validated. Whether feedback that follows a told grade changes what students
learn is untested here and needs a study with students. Several analyses suggested by the literature remain open: a
standard defense that marks the student's text as data, a downward and an argued push beside the upward one, a
mathematics reference answer with a planted error, feedback tone by group for the disability comparison, and the
energy of the trained scorers and of grading with feedback.

## 7. Threats to validity

### Construct validity

QWK depends on the rating scale and on how grades are distributed (Doewes, Kurdhi and Saxena 2023; Albatarni and
Elsayed 2026). The three text tasks use different scales, so the paper compares models within a task and reports
agreement as a share of the raters' agreement on the same items rather than comparing raw QWK across tasks.

The essay ceiling is the raters' published agreement before adjudication, not an agreement computed on the board's 100
essays, because ASAP 2.0 releases only the adjudicated grade. The essay shares of the ceiling therefore compare a
model on 100 essays with raters on a different set.

Every model was graded through one plain prompt. A prompt tuned for a model, graded examples or a rubric written for
the task can raise agreement substantially, so the agreement figures describe what a plain prompt achieves, not what a
model can achieve.

Every adversarial probe tries to raise the grade; none tries to lower it, and the pushback test uses one unargued objection. A model that holds against one objection may not hold against repeated or
argued pressure.

The feedback tone measure is a rule that counts praise and criticism phrases, validated against trained annotators on
tutoring replies to mathematics mistakes and then applied to grading feedback on short answers. The Withholding
Answers evaluator was validated on the same corpus but published for feedback on
writing in grades 6 to 12. Both
transfers are arguments, not measurements.

The mathematics solutions were written by a language model asked to make student-like errors, so the working effect
describes grading of simulated errors. The video measure removes the recording's length from both the model's grades
and the raters', and length carries real information about skill, so a verdict that a run adds nothing beyond length
does not show that the run ignored the video.

The surface features in the disability analysis are counted by fixed rules from a spelling dictionary and are proxies,
not validated measures of writing conventions.

### Internal validity

Hosted models were served by providers chosen at request time from those that retain no data (except as Section 4.3
states), and providers can serve
a model at different precisions or with different configurations. For the models served by many hosts, the board's
results mix those hosts. The hosting study and the controlled precision study address precision for a few models; the
other differences between hosts were not measured.

A model can give a different grade when asked the same question again, and some studies of settings ran each setup
once. The guard-sentence harms were re-tested against repeated runs, but the other single-run setup results were not.

The corpora are public, so a model may have seen their items in training. An exact search of one open model's training
data found some of the items (`code/contamination/`), and nothing is known about the training data of the closed
models. A private held-out set would address this.

### External validity

The text corpora come from one undergraduate course for short answers, one course for programs, and US school essays
for ASAP 2.0, all in English. The results describe these students and tasks, and may not hold for other subjects, ages
or languages.

The models were tested as their providers served them during the study. Models change between releases and sometimes
within one, so the results describe the versions named in Table 4.2.

The perception audit could test only open models, because the corpus's license does not allow sending a reduced copy
of a video and hosted endpoints refused most full-length videos. Beyond the works cited in Section 2.4, the literature on skin tone and
lighting in vision models was not reviewed for this paper.

### Statistical conclusion validity

Each task has 100 items, so many intervals are wide, and a verdict of no difference shown is not evidence of no
difference. The paper reports the size of the effect that could not be ruled out wherever a study computed it.

Many intervals are reported, so some exclude 0 by chance. The board's probe intervals were corrected for a false
discovery rate (Benjamini and Hochberg 1995), and the feedback study's verdicts likewise, but intervals from different
studies were not corrected jointly.

The four studies without verdict wording, and the six sets of statistics without a planted-effect check, are named
in Section 4.6. Many of the studies' numbered changes, in most of the studies, were made after some of that study's
own results had been read. The largest group of these only added models or graders, under the maintainer's decisions
on coverage, with no rule changed; others added an arm or a run, fixed a bug, added a reported statistic, or changed
what is scored or how a measure is read. One of the last kind is the board's feedback strand, which left out
the share of feedback that gives away the answer after every frontier model scored 96% to 100% on it
(`code/feedback-board/fb.py`, CHANGE 1); later, after the board's feedback results had been read, the way it
scored the halo was changed and the halo was then replaced by the wrong-grade test (Section 5.3). Those two later
changes have rows in `code/docs/CORRECTIONS.md`; they and the board's other unnumbered scoring changes, listed in
Section 4.6, are in the repository's commit history rather than numbered. Each
numbered change states when it was made; where it does not say what had been read, the study's committed outputs date
it. The release includes an inventory of every study's pre-registration, check and numbered changes, with the
board's unnumbered scoring changes (`preregistration-inventory.md`, beside the release file).

### Conflict of interest

The Learning Design Alliance, the author's organization, makes Lazuli, a product that grades student work and writes
feedback. Lazuli is not among the graders tested, and nothing from its prompts or results is used in the benchmark.
The research and writing were carried out with Claude Code, an AI system made by Anthropic, which also makes three of
the models tested (Claude Opus 5.5, Claude Fable 5.1 and Claude Haiku 5.5). Every result for those models comes from
the same code, prompt and checks as for the others.

## 8. Conclusion

Twenty-two language models were graded on short answers, programs and essays against expert raters, and then on
altered versions of the same work whose correct grade was known in advance. Most agree with the raters on short
answers about as well as the raters agree with each other, and no point estimate reaches the raters' published
agreement on essays, where a scorer trained on the corpus's graded essays has a higher point estimate. Agreement did
not show how a model behaves when the work, the context or the conversation is altered: a note in the answer moved the
grade by more than 5% of the scale for 14 of the 22 models as their hosts served them, most raised the grade more after a bare objection than
after a request to double-check, every model wrote feedback whose tone, as a word rule measures it, followed a wrong
grade it was told, and
most models that grade recordings gave credit to recordings with nothing to grade.

A grader's agreement with human raters is therefore one piece of evidence, and on its own it does not show that the
grader grades the work. The benchmark offers a way to gather the rest: probes with a known correct response, checked
on simulated graders before they are read, run on the grader as it will be deployed, and run again whenever its
prompt, its settings, its provider or its model changes.

## 9. Data, code and provenance

The code is the benchmark's repository, published with this release at the commit recorded in the release file. Paths
in this paper are relative to it and are written `code/<path>`. It holds every study's script and, for the speech,
handwriting and video tasks, a `PREREG.md` file; their opening text records the study's pre-registration, its
planted-effect check where it has one (Section 4.6), and its numbered changes (the board's unnumbered scoring changes
are listed in Section 4.6 by commit); each study's README; and each
study's committed outputs in its `out/` folder. Each model's grades on the board's items are in `code/submissions/`,
grades only. The corpora are not redistributed: each is fetched from its source, as listed in
`code/docs/DATA-SOURCES.md`, and the board's three corpora are checked against the hashes pinned in
`code/fetch_data.py`.

**Reproducing the results.** The numbers in Section 5 come from the committed outputs, and the report that
accompanies this paper recomputes from them, when it is built, every number it links: all but a few pre-registered
constants and figures quoted from the corpora's own papers. The re-run notebooks recompute each research
question's answer from those outputs. A study's analysis can be re-run from its graded runs with the command in its
README; sending the prompts again needs the corpora and a provider for each model, and can give different grades,
because hosted models change.

| result | study | script | `reproduce.py` step | notebook |
|---|---|---|---|---|
| Agreement, standard checks, length (5.1) | `code/leaderboard.py`, `code/analyses/` | `leaderboard.py build`, `analyses/standard_checks.py`, `analyses/length_partial.py` | `board`, `standard-checks`, `length` | `rq1-agreement` |
| Trained scorers (5.1) | `code/baselines/` | `baselines/baselines.py` | `baselines`, `scoring` (DeBERTa rows: GPU) | `rq1-agreement` |
| Essay fine-tunes (5.1 to 5.3) | `code/essays-finetune/`, `code/essays-genft/` | `essays-finetune/study.py analyse`, `essays-genft/study.py analyse` | `verify` (GPU) | `rq1-agreement` |
| Probes and flags (5.2) | `code/leaderboard.py` | `leaderboard.py build` | `board` | `rq2-robustness` |
| Settings: guard sentence, reasoning effort, hosts, precision, rewording (5.2) | `code/setups/`, `code/guard-retest/`, `code/reasoning/`, `code/hosting/`, `code/precision-controlled/`, `code/paraphrase/`, `code/prompt-ranking/` | each study's `study.py analyse` | `verify` (model calls) | `rq2-robustness` |
| Pushback, working, feedback (5.3) | `code/feedback-board/`, `code/maths-process/`, `code/feedback-validity/`, `code/feedback-discordant/` | `feedback-board/pushback.py analyse`, `maths-process/process.py analyse`, `feedback-discordant/study.py analyse` | `standard-checks`, `overall`; otherwise `verify` (model calls) | `rq3-beyond-the-grade` |
| Speech, languages, images, video, perception (5.4) | `code/speech/`, `code/language/`, `code/images/`, `code/video/`, `code/media/`, `code/perception/` | each study's README | `verify` (model calls) | `rq4-recordings` |
| Fairness and stability (5.5) | `code/fairness-ellipse/`, `code/disability/`, `code/disability-mechanism/`, `code/out/lineage-2026-10-23/` (described in `code/docs/DRIFT.md`) | each study's README; `bench.py drift` for the release comparison | `verify` (model calls) | `rq5-fairness-stability` |
| Energy and lifecycle (5.6) | `code/energy/`, `code/docs/LIFECYCLE.md` | `energy/energy.py analyse` | `verify` (GPU), `public` | `rq6-footprint` |

`reproduce.py` and `REPRODUCE.md` ship beside the release file. The script checks every committed output against the
hashes the release lists, fetches and checks the board's corpora, and re-runs each analysis that needs no model call,
comparing its output with the committed one. An analysis that needs model calls or a GPU is checked only through its
committed outputs (`verify`), because the models' replies are not published.

**What is not published, and why.** The corpora's student work, recordings and images are not published, because
their licenses do not allow redistribution or because they show identifiable people. The models' replies and the
run logs are not published, because they quote and paraphrase that work; the grades taken from them are. No prompt
or result from any product is in the repository, Lazuli's included.

## AI use

I, David Porcaro, orchestrated the development of this report. I asked the questions that drove this benchmark study,
pointed the coding agent to methods, articles, and datasets and responded to questions. I supervised errors and made
decisions on fixes.

I did not write the methods or code, I did not write the report itself, nor did I review all the prior research cited.
I do not claim to have done anything I did not.

I did review every line of the final report to make sure I understood the background, methods and results, and only
signed off when I had successfully answered questions about the headline results and findings from the agent.

## References

> **How the references were checked.** Every entry was resolved by an agent against a primary record: Crossref,
> DataCite, the ACL Anthology, arXiv, PMLR, or the publisher's own document (the two reports). Preprints are marked.
> Seventeen entries were found and resolved by an agent independent of the draft, in a review of prior work, and
> re-resolved when they were added; the others have not yet been re-checked independently.

- Albatarni, S., & Elsayed, T. (2026). Quadratic weighted kappa is not enough for evaluating automated essay scoring models. In *Proceedings of the Fifteenth Language Resources and Evaluation Conference* (pp. 4447–4456). ELRA. <https://aclanthology.org/2026.lrec-1.348/>
- Arvin, C. (2025). "Check my work?": Measuring sycophancy in a simulated educational context. arXiv:2506.10297 (preprint). <https://arxiv.org/abs/2506.10297>
- Atil, B., Aykent, S., Chittams, A., et al. (2024). Non-determinism of "deterministic" LLM settings. arXiv:2408.04667 (preprint). <https://arxiv.org/abs/2408.04667>
- Bagdasaryan, E., Hsieh, T.-Y., Nassi, B., & Shmatikov, V. (2023). (Ab)using images and sounds for indirect instruction injection in multi-modal LLMs. arXiv:2307.10490 (preprint). <https://arxiv.org/abs/2307.10490>
- Baker, R. S., & Hawn, A. (2022). Algorithmic bias in education. *International Journal of Artificial Intelligence in Education*, 32(4), 1052–1092. <https://doi.org/10.1007/s40593-021-00285-9>
- Barrus, T. (2024). *pyspellchecker* (Version 0.8.1) [Computer software]. <https://github.com/barrust/pyspellchecker>
- Bavaresco, A., Bernardi, R., Bertolazzi, L., et al. (2025). LLMs instead of human judges? A large scale empirical study across 20 NLP evaluation tasks. arXiv:2406.18403 (preprint). <https://arxiv.org/abs/2406.18403> (ACL 2025 per the authors)
- Bellibatlu, R. R., Raff, E., & Zhang, W. (2026). JudgeSense: A benchmark for prompt sensitivity in LLM-as-a-judge systems. arXiv:2604.23478 (preprint). <https://arxiv.org/abs/2604.23478>
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological)*, 57(1), 289–300. <https://doi.org/10.1111/j.2517-6161.1995.tb02031.x>
- Beyene, L. H., Verma, V., Ma, M., Alabi, J. O., Schmidt, F. D., Nakatumba-Nabende, J., & Adelani, D. I. (2025). mSTEB: Massively multilingual evaluation of LLMs on speech and text tasks. arXiv:2506.08400 (preprint). <https://arxiv.org/abs/2506.08400>
- Bieker, G. (2021). *A global comparison of the life-cycle greenhouse gas emissions of combustion engine and electric passenger cars* (White paper). International Council on Clean Transportation. <https://theicct.org/wp-content/uploads/2021/12/Global-LCA-passenger-cars-jul2021_0.pdf>
- Bridgeman, B., Trapani, C., & Attali, Y. (2012). Comparison of human and machine scoring of essays: Differences by gender, ethnicity, and country. *Applied Measurement in Education*, 25(1), 27–40. <https://doi.org/10.1080/08957347.2012.635502>
- Buch, S., Eyzaguirre, C., Gaidon, A., Wu, J., Fei-Fei, L., & Niebles, J. C. (2022). Revisiting the "video" in video-language understanding. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2022)* (pp. 2917–2927). <https://openaccess.thecvf.com/content/CVPR2022/html/Buch_Revisiting_the_Video_in_Video-Language_Understanding_CVPR_2022_paper.html>
- Bulut, O., Tan, B., Mazzullo, E., & Walsh, C. (2026). The scoring paradox: Multi-agent architectures for unbiased feedback optimization. In *Proceedings of AIME-Con 2026: Coordinated Session Papers* (pp. 274–283). <https://aclanthology.org/2026.aimecon-sessions.30/>
- Buolamwini, J., & Gebru, T. (2018). Gender shades: Intersectional accuracy disparities in commercial gender classification. In *Proceedings of the 1st Conference on Fairness, Accountability and Transparency* (PMLR 81, pp. 77–91). <https://proceedings.mlr.press/v81/buolamwini18a.html>
- Buzick, H., Oliveri, M. E., Attali, Y., & Flor, M. (2016). Comparing human and automated essay scoring for prospective graduate students with learning disabilities and/or ADHD. *Applied Measurement in Education*, 29(3), 161–172. <https://doi.org/10.1080/08957347.2016.1171765>
- Calderon, N., Reichart, R., & Dror, R. (2025). The alternative annotator test for LLM-as-a-judge: How to statistically justify replacing human annotators with LLMs. arXiv:2501.10970 (preprint). <https://arxiv.org/abs/2501.10970>
- Carbon Trust. (2021). *Carbon impact of video streaming* (White paper). <https://www.carbontrust.com/sites/default/files/documents/resource/public/Carbon-impact-of-video-streaming.pdf>
- Chamieh, I., Zesch, T., & Giebermann, K. (2024). LLMs in short answer scoring: Limitations and promise of zero-shot and few-shot approaches. In *Proceedings of the 19th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2024)* (pp. 309–315). ACL. <https://aclanthology.org/2024.bea-1.25/>
- Chen, L., Li, J., Dong, X., et al. (2024). Are we on the right way for evaluating large vision-language models? <https://arxiv.org/abs/2403.20330> (arXiv:2403.20330; NeurIPS 2024)
- Chen, L., Zaharia, M., & Zou, J. (2024). How is ChatGPT's behavior changing over time? *Harvard Data Science Review*, 6(2). <https://doi.org/10.1162/99608f92.5317da47>
- Chen, Y., Hu, X., Yin, K., Li, J., & Zhang, S. (2025). Evaluating the robustness of multimodal agents against active environmental injection attacks. arXiv:2502.13053 (preprint). <https://arxiv.org/abs/2502.13053> (ACM MM 2025 per the authors)
- Cheng, H., Xiao, E., Wang, Y., Zhang, L., Zhang, Q., Cao, J., Xu, K., Sun, M., et al. (2025). Exploring typographic visual prompts injection threats in cross-modality generation models. arXiv:2503.11519 (preprint). <https://arxiv.org/abs/2503.11519>
- Chodorow, M., & Burstein, J. (2004). Beyond essay length: Evaluating e-rater's performance on TOEFL essays. *ETS Research Report Series*, 2004(1). <https://doi.org/10.1002/j.2333-8504.2004.tb01931.x>
- Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., & Schulman, J. (2021). Training verifiers to solve math word problems. arXiv:2110.14168 (preprint). <https://arxiv.org/abs/2110.14168>
- Conneau, A., Ma, M., Khanuja, S., Zhang, Y., Axelrod, V., Dalmia, S., Riesa, J., Rivera, C., & Bapna, A. (2023). FLEURS: Few-shot learning evaluation of universal representations of speech. In *2022 IEEE Spoken Language Technology Workshop (SLT)* (pp. 798–805). IEEE. <https://doi.org/10.1109/SLT54892.2023.10023141>
- Conway, D. A., & Roberts, H. V. (1983). Reverse regression, fairness, and employment discrimination. *Journal of Business & Economic Statistics*, 1(1), 75–85. <https://doi.org/10.1080/07350015.1983.10509326>
- Cooper, A. F., et al. (2024). Arbitrariness and social prediction: The confounding role of variance in fair classification. arXiv:2301.11562 (preprint). <https://arxiv.org/abs/2301.11562> (AAAI 2024 per the authors)
- Crossley, S., Baffour, P., Burleigh, L., & King, J. (2025). A large-scale corpus for assessing source-based writing quality: ASAP 2.0. *Assessing Writing*, 65, 100954. <https://doi.org/10.1016/j.asw.2025.100954>
- Crossley, S., Tian, Y., Baffour, P., Franklin, A., Kim, Y., Morris, W., Benner, M., Picou, A., & Boser, U. (2023). The English Language Learner Insight, Proficiency and Skills Evaluation (ELLIPSE) corpus. *International Journal of Learner Corpus Research*, 9(2), 248–269. <https://doi.org/10.1075/ijlcr.22026.cro>
- Daheim, N., Macina, J., Kapur, M., Gurevych, I., & Sachan, M. (2024). Stepwise verification and remediation of student reasoning errors with large language model tutors. In *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing* (pp. 8386–8411). ACL. <https://doi.org/10.18653/v1/2024.emnlp-main.478>
- Ding, Y., Riordan, B., Horbach, A., Cahill, A., & Zesch, T. (2020). Don't take "nswvtnvakgxpm" for an answer – The surprising vulnerability of automatic content scoring systems to adversarial input. In *Proceedings of the 28th International Conference on Computational Linguistics (COLING 2020)* (pp. 882–892). <https://doi.org/10.18653/v1/2020.coling-main.76>
- Doewes, A., Kurdhi, N. A., & Saxena, A. (2023). Evaluating quadratic weighted kappa as the standard performance metric for automated essay scoring. In *Proceedings of the 16th International Conference on Educational Data Mining* (pp. 103–113). <https://educationaldatamining.org/EDM2023/proceedings/2023.EDM-long-papers.9/index.html>
- Elsworth, C., Huang, K., Patterson, D., et al. (2025). Measuring the environmental impact of delivering AI at Google scale. arXiv:2508.15734 (preprint). <https://arxiv.org/abs/2508.15734>
- Fanous, A., Goldberg, J., Agarwal, A. A., et al. (2025). SycEval: Evaluating LLM sycophancy. arXiv:2502.08177 (preprint). <https://arxiv.org/abs/2502.08177>
- Fernandez, J., Na, C., Tiwari, V., Bisk, Y., Luccioni, S., & Strubell, E. (2025). Energy considerations of large language model inference and efficiency optimizations. arXiv:2504.17674 (preprint). <https://arxiv.org/abs/2504.17674>
- Ferreira Mello, R., Pereira Junior, C., Rodrigues, L., et al. (2025). Automatic short answer grading in the LLM era: Does GPT-4 with prompt engineering beat traditional models? In *Proceedings of the 15th International Learning Analytics and Knowledge Conference (LAK '25)* (pp. 93–103). <https://doi.org/10.1145/3706468.3706481>
- Filighera, A., Steuer, T., & Rensing, C. (2020). Fooling automatic short answer grading systems. In *Artificial Intelligence in Education (AIED 2020)* (pp. 177–190). Springer. <https://doi.org/10.1007/978-3-030-52237-7_15>
- Foo, L. H.-Y., Yang, C.-K., Li, C.-A., Lu, K.-H., & Lee, H.-y. (2026). All that glitters is not audio: Rethinking text priors and audio reliance in audio-language evaluation. arXiv:2604.24401 (preprint). <https://arxiv.org/abs/2604.24401>
- Funke, I., Bodenstedt, S., von Bechtolsheim, F., Oehme, F., Maruschke, M., Herrlich, S., Weitz, J., Distler, M., Mees, S. T., & Speidel, S. (2026). A benchmark for video-based laparoscopic skill analysis and assessment. arXiv:2602.09927 (preprint). <https://arxiv.org/abs/2602.09927>
- Gao, I., Liang, P., & Guestrin, C. (2025). Model equality testing: Which model is this API serving? arXiv:2410.20247 (preprint). <https://arxiv.org/abs/2410.20247> (ICLR 2025 per the authors)
- Goh, G., Cammarata, N., Voss, C., Carter, S., Petrov, M., Schubert, L., Radford, A., & Olah, C. (2021). Multimodal neurons in artificial neural networks. *Distill*, 6(3). <https://doi.org/10.23915/distill.00030>
- Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., & Fritz, M. (2023). Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. In *Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security* (pp. 79–90). <https://doi.org/10.1145/3605764.3623985>
- Gupta, U., Kim, Y. G., Lee, S., et al. (2021). Chasing carbon: The elusive environmental footprint of computing. In *Proceedings of the 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA)* (pp. 854–867). <https://doi.org/10.1109/HPCA51647.2021.00076>
- Hattie, J., & Timperley, H. (2007). The power of feedback. *Review of Educational Research*, 77(1), 81–112. <https://doi.org/10.3102/003465430298487>
- Hazirbas, C., Bitton, J., Dolhansky, B., Pan, J., Gordo, A., & Canton Ferrer, C. (2022). Towards measuring fairness in AI: The Casual Conversations dataset. *IEEE Transactions on Biometrics, Behavior, and Identity Science*, 4(3), 324–332. <https://doi.org/10.1109/TBIOM.2021.3132237>
- He, P., Gao, J., & Chen, W. (2021). DeBERTaV3: Improving DeBERTa using ELECTRA-style pre-training with gradient-disentangled embedding sharing. arXiv:2111.09543 (preprint). <https://arxiv.org/abs/2111.09543>
- Heilman, M., & Madnani, N. (2015). The impact of training data on automated short answer scoring performance. In *Proceedings of the Tenth Workshop on Innovative Use of NLP for Building Educational Applications* (pp. 81–85). ACL. <https://doi.org/10.3115/v1/W15-0610>
- Hines, K., Lopez, G., Hall, M., Zarfati, F., Zunger, Y., & Kiciman, E. (2024). Defending against indirect prompt injection attacks with spotlighting. arXiv:2403.14720 (preprint). <https://arxiv.org/abs/2403.14720>
- Hong, J., Duan, J., Zhang, C., et al. (2024). Decoding compressed trust: Scrutinizing the trustworthiness of efficient LLMs under compression. arXiv:2403.15447 (preprint). <https://arxiv.org/abs/2403.15447> (ICML 2024 per the authors)
- Huang, Y., Palermo, C., & Wilson, J. (2026). Accuracy and fairness of generative AI in automated essay scoring: Comparing GPT-4o, feature-based models, and human raters. *Assessing Writing*, 69, 101047. <https://doi.org/10.1016/j.asw.2026.101047>
- Hwang, Y., Lee, D., Kang, T., Kim, Y., & Jung, K. (2025). Can you trick the grader? Adversarial persuasion of LLM judges. arXiv:2508.07805 (preprint). <https://arxiv.org/abs/2508.07805>
- Jegham, N., Abdelatti, M., Koh, C. Y., Elmoubarki, L., & Hendawi, A. (2025). How hungry is AI? Benchmarking energy, water, and carbon footprint of LLM inference. arXiv:2505.09598 (preprint). <https://arxiv.org/abs/2505.09598>
- Johnson, M. S., Liu, X., & McCaffrey, D. F. (2022). Psychometric methods to evaluate measurement and algorithmic bias in automated scoring. *Journal of Educational Measurement*, 59(3), 338–361. <https://doi.org/10.1111/jedm.12335>
- Jukiewicz, M. (2026). A systematic comparison of large language models for automated assignment assessment in programming education: Exploring the importance of architecture and vendor. *Computers and Education Open*, 10, 100364. <https://doi.org/10.1016/j.caeo.2026.100364>
- Kabra, A., Bhatia, M., Singla, Y. K., Li, J. J., & Shah, R. R. (2022). Evaluation toolkit for robustness testing of automatic essay scoring systems. In *Proceedings of the 5th Joint International Conference on Data Science & Management of Data (CODS-COMAD 2022)* (pp. 90–99). <https://doi.org/10.1145/3493700.3493765>
- Kapetanovic, A., Altwlkany, K., Mercep, A., Duricic, T., & Lacic, E. (2026). Anchoring bias in LLM-as-a-judge systems: Prior scores compromise evaluation independence. arXiv:2608.25869 (preprint). <https://arxiv.org/abs/2608.25869> (CIKM '26 per the authors)
- Karjus, A., Allkivi, K., Maine, S., Leppik, K., Kruusmaa, K., & Aruvee, M. (2026). Machine-assisted grading of nationwide school-leaving essay exams with LLMs and statistical NLP. arXiv:2601.16314 (preprint). <https://arxiv.org/abs/2601.16314>
- Kelly, J. D., Petersen, A., Lendvay, T. S., & Kowalewski, T. M. (2020). The effect of video playback speed on surgeon technical skill perception. *International Journal of Computer Assisted Radiology and Surgery*, 15, 739–747. <https://doi.org/10.1007/s11548-020-02134-x>
- Khrulev, R. (2025). CHECK-MAT: Probing the mathematical reasoning and rubric-alignment of vision-language models on handwritten solutions. In *Proceedings of the 3rd Workshop on Mathematical Natural Language Processing (MathNLP 2025)* (pp. 77–94). ACL. <https://doi.org/10.18653/v1/2025.mathnlp-main.6>
- Kim, S., & Khashabi, D. (2025). Challenging the evaluator: LLM sycophancy under user rebuttal. arXiv:2509.16533 (preprint). <https://arxiv.org/abs/2509.16533>
- Koenecke, A., Choi, A. S. G., Mei, K. X., Schellmann, H., & Sloane, M. (2024). Careless Whisper: Speech-to-text hallucination harms. In *Proceedings of the 2024 ACM Conference on Fairness, Accountability, and Transparency (FAccT '24)*. <https://doi.org/10.1145/3630106.3658996>
- Kortemeyer, G. (2023). Performance of the pre-trained large language model GPT-4 on automated short answer grading. arXiv:2309.09338 (preprint). <https://arxiv.org/abs/2309.09338>
- Kucia, F. J., Chakraborty, A., & Wróblewska, A. (2026). LLM essay scoring under holistic and analytic rubrics: Prompt effects and bias. arXiv:2604.00259 (preprint). <https://arxiv.org/abs/2604.00259> (ICCS 2026 per the authors)
- Kundu, A., & Barbosa, D. (2024). Are large language models good essay graders? arXiv:2409.13120 (preprint). <https://arxiv.org/abs/2409.13120>
- Kwako, A., & Ormerod, C. (2024). Can language models guess your identity? Analyzing demographic biases in AI essay scoring. In *Proceedings of the 19th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2024)* (pp. 78–86). ACL. <https://aclanthology.org/2024.bea-1.7/>
- Laban, P., Murakhovs'ka, L., Xiong, C., & Wu, C.-S. (2023). Are you sure? Challenging LLMs leads to performance drops in the FlipFlop experiment. arXiv:2311.08596 (preprint). <https://arxiv.org/abs/2311.08596>
- Latif, E., & Zhai, X. (2024). Fine-tuning ChatGPT for automatic scoring. *Computers and Education: Artificial Intelligence*, 6, 100210. <https://doi.org/10.1016/j.caeai.2024.100210>
- Learning Commons. (2025). *Evaluators* [Computer software]. GitHub. <https://github.com/learning-commons-org/evaluators>
- Li, H., Filippov, F., Lin, Y., et al. (2026). "\*\*Important\*\* You should give me full credits!": Exploring prompt injection attacks on LLM-based automatic grading systems. arXiv:2606.03090 (preprint). <https://arxiv.org/abs/2606.03090>
- Li, P., Yang, J., Islam, M. A., & Ren, S. (2025). Making AI less "thirsty". *Communications of the ACM*, 68(7), 54–61. <https://doi.org/10.1145/3724499>
- Li, S., Xu, C., Wang, J., et al. (2025). LLMs cannot reliably judge (yet?): A comprehensive assessment on the robustness of LLM-as-a-judge. arXiv:2506.09443 (preprint). <https://arxiv.org/abs/2506.09443>
- Li, X., Zhou, Z., Liu, Z., & Wu, Y. (2026). GradingAttack: Exposing security vulnerabilities in LLM based educational grading agents. arXiv:2602.00979 (preprint). <https://arxiv.org/abs/2602.00979>
- Lightman, H., Kosaraju, V., Burda, Y., Edwards, H., et al. (2023). Let's verify step by step. <https://arxiv.org/abs/2305.20050> (arXiv:2305.20050, preprint)
- Luccioni, A. S., Strubell, E., & Crawford, K. (2025). From efficiency gains to rebound effects: The problem of Jevons' paradox in AI's polarized environmental debate. arXiv:2501.16548 (preprint). <https://arxiv.org/abs/2501.16548> (FAccT '25 per the authors)
- Luccioni, S., Gamazaychikov, B., Alves da Costa, T., & Strubell, E. (2025). Misinformation by omission: The need for more environmental transparency in AI. arXiv:2506.15572 (preprint). <https://arxiv.org/abs/2506.15572>
- Luccioni, S., Jernite, Y., & Strubell, E. (2024). Power hungry processing: Watts driving the cost of AI deployment? In *Proceedings of the 2024 ACM Conference on Fairness, Accountability, and Transparency (FAccT '24)* (pp. 85–99). <https://doi.org/10.1145/3630106.3658542>
- Luo, Y., Yang, Z., Meng, F., Li, Y., Zhou, J., & Zhang, Y. (2023). An empirical study of catastrophic forgetting in large language models during continual fine-tuning. arXiv:2308.08747 (preprint). <https://arxiv.org/abs/2308.08747>
- Macina, J., Daheim, N., Chowdhury, S. P., Sinha, T., Kapur, M., Gurevych, I., & Sachan, M. (2023). MathDial: A dialogue tutoring dataset with rich pedagogical properties grounded in math reasoning problems. In *Findings of the Association for Computational Linguistics: EMNLP 2023* (pp. 5602–5621). ACL. <https://doi.org/10.18653/v1/2023.findings-emnlp.372>
- Malouff, J. M., & Thorsteinsson, E. B. (2016). Bias in grading: A meta-analysis of experimental research findings. *Australian Journal of Education*, 60(3), 245–256. <https://doi.org/10.1177/0004944116664618>
- Maurya, K. K., Srivatsa, K. A., Petukhova, K., & Kochmar, E. (2025). Unifying AI tutor evaluation: An evaluation taxonomy for pedagogical ability assessment of LLM-powered AI tutors. In *Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)* (pp. 1234–1251). ACL. <https://doi.org/10.18653/v1/2025.naacl-long.57>
- Mendonça, P. C., Quintal, F., Mendonça, F., & Baras, K. (2026). *The HARMOGEN-R dataset of human and AI-generated rubric evaluations for formative programming assessment* (Version 2.0) [Data set]. Zenodo. <https://doi.org/10.5281/zenodo.19534458>
- Meyer, G., Breuer, P., & Fürst, J. (2024). ASAG2024: A combined benchmark for short answer grading. arXiv:2409.18596 (preprint). <https://arxiv.org/abs/2409.18596>
- Mizrahi, M., Kaplan, G., Malkin, D., Dror, R., Shahaf, D., & Stanovsky, G. (2024). State of what art? A call for multi-prompt LLM evaluation. *Transactions of the Association for Computational Linguistics*, 12, 933–949. <https://doi.org/10.1162/tacl_a_00681>
- Mohler, M., Bunescu, R., & Mihalcea, R. (2011). Learning to grade short answer questions using semantic similarity measures and dependency graph alignments. In *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics: Human Language Technologies* (pp. 752–762). ACL. <https://aclanthology.org/P11-1076/>
- Morris, T. P., White, I. R., & Crowther, M. J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine*, 38(11), 2074–2102. <https://doi.org/10.1002/sim.8086>
- Nguyen, D. S., Dang, Q. M., Nguyen, H. L., Truong, V. V., & Nguyen, T. A. (2026). How far can sub-3B open language models go in zero-shot essay scoring on an 8 GB consumer GPU? arXiv:2609.20250 (preprint). <https://arxiv.org/abs/2609.20250>
- Ormerod, C., & Kehat, G. (2025). Long context automated essay scoring with language models. arXiv:2509.10417 (preprint). <https://arxiv.org/abs/2509.10417>
- Oviedo, F., Kazhamiaka, F., Choukse, E., et al. (2026). Energy use of AI inference, efficiency pathways, and test-time scaling. *Joule*, 10(8), 102430. <https://doi.org/10.1016/j.joule.2026.102430>
- Pack, A., Barrett, A., & Escalante, J. (2024). Large language models and automated essay scoring of English language learner writing: Insights into validity and reliability. *Computers and Education: Artificial Intelligence*, 6, 100234. <https://doi.org/10.1016/j.caeai.2024.100234>
- Parikh, A. K., Tejedor-Garcia, C., Cucchiarini, C., & Strik, H. (2025). Zero-shot speech LLMs for multi-aspect evaluation of L2 speech: Challenges and opportunities. In *Proceedings of SLaTE 2025*. <https://doi.org/10.21437/SLaTE.2025-3>
- Perez, E., Ringer, S., Lukošiūtė, K., et al. (2022). Discovering language model behaviors with model-written evaluations. arXiv:2212.09251 (preprint). <https://arxiv.org/abs/2212.09251>
- Poore, J., & Nemecek, T. (2018). Reducing food's environmental impacts through producers and consumers. *Science*, 360(6392), 987–992. <https://doi.org/10.1126/science.aaq0216>
- Porcaro, D. S. (2026). *Reliability, calibration and attack surface of an LLM short-answer grader, measured against three human-graded corpora* (Research release ai-grader-reliability-2026, version 1.0.0, whose article is "Learner context changes an LLM grader's marks on identical work: a within-item ablation on six models"). Zenodo. <https://doi.org/10.5281/zenodo.23480844>
- Porgali, B., Albiero, V., Ryda, J., Canton Ferrer, C., & Hazirbas, C. (2023). The Casual Conversations v2 dataset. arXiv:2303.04838 (preprint). <https://arxiv.org/abs/2303.04838>
- Powers, D. E., Burstein, J. C., Chodorow, M., Fowles, M. E., & Kukich, K. (2002). Stumping e-rater: Challenging the validity of automated essay scoring. *Computers in Human Behavior*, 18(2), 103–134. <https://doi.org/10.1016/S0747-5632%2801%2900052-8>
- Qi, X., Zeng, Y., Xie, T., Chen, P.-Y., Jia, R., Mittal, P., & Henderson, P. (2023). Fine-tuning aligned language models compromises safety, even when users do not intend to! arXiv:2310.03693 (preprint). <https://arxiv.org/abs/2310.03693>
- Raina, V., Liusie, A., & Gales, M. (2024). Is LLM-as-a-judge robust? Investigating universal adversarial attacks on zero-shot LLM assessment. In *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing* (pp. 7499–7517). ACL. <https://doi.org/10.18653/v1/2024.emnlp-main.427>
- Rau, A., Endo, M., Aklilu, J., et al. (2025). Systematic evaluation of large vision-language models for surgical artificial intelligence. arXiv:2504.02799 (preprint). <https://arxiv.org/abs/2504.02799>
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. <https://arxiv.org/abs/1908.10084> (arXiv:1908.10084; EMNLP 2019)
- Ribeiro, M. T., Wu, T., Guestrin, C., & Singh, S. (2020). Beyond accuracy: Behavioral testing of NLP models with CheckList. In *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics* (pp. 4902–4912). ACL. <https://doi.org/10.18653/v1/2020.acl-main.442>
- Sahoo, D., Prasad, M., Majhi, V., Neekhra, A., Sinha, Y., Mandal, M., Chamola, V., & Kumar, D. (2026). The compliance paradox: Semantic-instruction decoupling in automated academic code evaluation. arXiv:2601.21360 (preprint). <https://arxiv.org/abs/2601.21360>
- Sakunkoo, A., & Sakunkoo, J. (2025). Name of thrones: How do LLMs rank student names in status hierarchies based on race and gender? In *Proceedings of the 20th Workshop on Innovative Use of NLP for Building Educational Applications* (pp. 697–707). ACL. <https://doi.org/10.18653/v1/2025.bea-1.50>
- Schmidt, F. D., Vulić, I., Glavaš, G., & Adelani, D. I. (2025). Fleurs-SLU: A massively multilingual benchmark for spoken language understanding. arXiv:2501.06117 (preprint). <https://arxiv.org/abs/2501.06117>
- Schumann, C., Olanubi, G. O., Wright, A., Monk, E., Heldreth, C., & Ricco, S. (2023). Consensus and subjectivity of skin tone annotation for ML fairness. arXiv:2305.09073 (preprint). <https://arxiv.org/abs/2305.09073>
- Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). Quantifying language models' sensitivity to spurious features in prompt design or: How I learned to start worrying about prompt formatting. arXiv:2310.11324 (preprint). <https://arxiv.org/abs/2310.11324> (ICLR 2024 per the authors)
- Seßler, K., Fürstenberg, M., Bühler, B., & Kasneci, E. (2025). Can AI grade your essays? A comparative analysis of large language models and teacher ratings in multidimensional essay scoring. arXiv:2411.16337 (preprint). <https://arxiv.org/abs/2411.16337> (LAK '25 per the authors)
- Sharma, M., Tong, M., Korbak, T., et al. (2023). Towards understanding sycophancy in language models. arXiv:2310.13548 (preprint). <https://arxiv.org/abs/2310.13548>
- Srivastava, M., Nushi, B., Kamar, E., Shah, S., & Horvitz, E. (2020). An empirical analysis of backward compatibility in machine learning systems. In *Proceedings of the 26th ACM SIGKDD Conference on Knowledge Discovery and Data Mining* (pp. 3272–3280). <https://doi.org/10.1145/3394486.3403379>
- Srivatsa, K. A., Maurya, K. K., & Kochmar, E. (2025). LLMs cannot spot math errors, even when allowed to peek into the solution. In *Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing* (pp. 10914–10928). ACL. <https://doi.org/10.18653/v1/2025.emnlp-main.553>
- Sunkavalli, V. K. (2026). LLM judges as raters: A pre-registered audit of severity, halo, reliability, and version instability in LLM essay scoring on public corpora. arXiv:2608.29517 (preprint). <https://arxiv.org/abs/2608.29517>
- Tan, M., Phalen, L., & Demszky, D. (2026). Marked pedagogies: Examining linguistic biases in personalized automated writing feedback. In *Proceedings of the 16th International Learning Analytics and Knowledge Conference (LAK26)* (pp. 568–577). <https://doi.org/10.1145/3785022.3785113> (arXiv:2603.12471)
- The Learning Agency. (2024). *ASAP 2.0* [Data set]. Kaggle. <https://www.kaggle.com/datasets/lburleigh/asap-2-0>
- Wallace, E., Xiao, K., Leike, R., Weng, L., Heidecke, J., & Beutel, A. (2024). The instruction hierarchy: Training LLMs to prioritize privileged instructions. arXiv:2404.13208 (preprint). <https://arxiv.org/abs/2404.13208>
- Wang, K., He, L., Liu, K., Deng, Y., Wei, W., & Zhao, S. (2025). Exploring the potential of large multimodal models as effective alternatives for pronunciation assessment. arXiv:2503.11229 (preprint). <https://arxiv.org/abs/2503.11229>
- Wang, W., Wei, F., Dong, L., Bao, H., Yang, N., & Zhou, M. (2020). MiniLM: Deep self-attention distillation for task-agnostic compression of pre-trained transformers. <https://arxiv.org/abs/2002.10957> (arXiv:2002.10957; NeurIPS 2020)
- Wang, Y., Hu, R., & Zhao, Z. (2024). Beyond agreement: Diagnosing the rationale alignment of automated essay scoring methods based on linguistically-informed counterfactuals. In *Findings of the Association for Computational Linguistics: EMNLP 2024* (pp. 8906–8925). ACL. <https://doi.org/10.18653/v1/2024.findings-emnlp.520>
- Williamson, D. M., Xi, X., & Breyer, F. J. (2012). A framework for evaluation and use of automated scoring. *Educational Measurement: Issues and Practice*, 31(1), 2–13. <https://doi.org/10.1111/j.1745-3992.2011.00223.x>
- Wood, S., Yao, E., Haisfield, L., & Lottridge, S. (2021). *Establishing standards of best practice in automated scoring* (Technical brief). ACT. <https://act.org/content/dam/act/unsecured/documents/R2100-auto-scoring-standards-2021-07.pdf>
- Wu, T., Xiang, C., Wang, J. T., et al. (2025). Does more inference-time compute really help robustness? arXiv:2507.15974 (preprint). <https://arxiv.org/abs/2507.15974>
- Zaremba, W., Nitishinskaya, E., Barak, B., et al. (2025). Trading inference-time compute for adversarial robustness. arXiv:2501.18841 (preprint). <https://arxiv.org/abs/2501.18841>
- Zhang, J., Zhang, Z., Wang, Y., Yan, Z., Song, Q., Huang, Y., Li, K., Povey, D., & Wang, Y. (2021). speechocean762: An open-source non-native English speech corpus for pronunciation assessment. In *Proceedings of Interspeech 2021* (pp. 3710–3714). ISCA. <https://doi.org/10.21437/Interspeech.2021-1259>
- Zheng, G., Wei, S., & Kandanaarachchi, S. (2026). LLM judges are easier to talk down than up: A Bayesian item response analysis. NeurIPS 2026 Workshop "Can We Trust AI Evaluation?" (poster). <https://neurips.cc/virtual/2026/178351>
- Zheng, X., Pang, T., Du, C., Liu, Q., Jiang, J., & Lin, M. (2025). Cheating automatic LLM benchmarks: Null models achieve high win rates. arXiv:2410.07137 (preprint). <https://arxiv.org/abs/2410.07137> (ICLR 2025 per the authors)
- Zverev, E., Abdelnabi, S., Tabesh, S., Fritz, M., & Lampert, C. H. (2025). Can LLMs separate instructions from data? And what do we even mean by that? arXiv:2403.06833 (preprint). <https://arxiv.org/abs/2403.06833> (ICLR 2025 per the authors)
