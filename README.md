# Russia university admission difficulty

Ranks Russian universities and fields of study by the exam score they admit on.
Nothing here reflects research output or reputation.

## The admission system

Almost every route into a Russian bachelor's or specialist programme runs on
one score. School leavers sit the ЕГЭ in their final year, each subject marked
out of 100, and a university admits on the total of the three or four subjects
its programme names. It then publishes ranked competition lists, so a place is
won against the other applicants rather than against a fixed bar.

A place is either бюджетное, paid by the state, or платное, paid by the
student, and the two are separate competitions with separate results.

The budget places are not one competition either. Olympiad winners take theirs
without sitting an exam at all, and the quotas — целевой приём for an employer
who has signed the student, особая квота for orphans and the disabled, and
since 2023 отдельная квота for the families of serving soldiers — each run
their own ranking at their own bar. The monitoring counted them separately
until 2017 and has published one blended number since.

| Route | What it ranks on | 2017 | 2025 |
| --- | --- | ---: | ---: |
| Общий конкурс | ЕГЭ total, minus achievement points | 216,545 | — |
| Олимпиады (БВИ) | An olympiad result; no exam is sat | 4,016 | 9,207 |
| Особая квота | ЕГЭ, ranked inside the quota | 12,103 | — |
| Целевой приём | ЕГЭ, ranked inside the employer's quota | 37,326 | — |
| **Бюджетные места** | | **269,994** | **357,439** |
| Платные места | ЕГЭ total, or the university's own test | 156,271 | 227,429 |
| **Full-time first degree** | | **426,265** | **584,868** |

`coverage.py` writes `data/source-coverage.tsv`, which records what each
mirrored page publishes, including the columns the ranking does not read.

## What is out of scope

The monitoring is a survey of full-time first-degree places won on the ЕГЭ,
which leaves out most of the ways a Russian school leaver continues. Nothing
here covers среднее профессиональное образование, the colleges and техникумы
that take students after the ninth grade and select on the school-leaving
certificate rather than the ЕГЭ; nor заочное and очно-заочное study, nor
master's programmes, nor the military, police and arts institutions the
monitoring excludes by design. Admission to a university on a college diploma
rather than an exam result is inside the headcount and outside the score.

## The source

HSE has published the Мониторинг качества приема every year since 2010. It
collects the admission lists off every university's own site, recomputes one
number per admitted student — the competition total divided by the number of
subjects counted, with achievement points taken out where they are visible —
and averages that into a score per university and per field of study. It
covers every institution admitting on the ЕГЭ, excluding the military and
performing-arts ones, and only full-time first-degree places.

`fetch/hse.py` mirrors both report families for every year the site indexes,
2011 through 2025, and `parse/hse.py` reads them into `data/admissions-*.tsv`,
809 universities across 66 укрупнённые группы in 2025 alone. Captions are
reworded almost every year, and each average is reprinted beside two decoys —
the same average with the achievement points left in, and the score of the
weakest admitted student — so `parse.hse` matches a column by the role its
caption describes rather than by its text. Several years also link a table
already filtered to universities above a size, which `fetch.hse` drops.

The monitoring gives a student admitted without exams a nominal 100 in every
subject. That is a placeholder, not a measurement, and at the most selective
universities it moves the average by several points, so `lib/admissions.py`
takes those students back out of the average and leaves them in the headcount.
Every table here ranks on `scored_mean`, the average over students who
actually sat the subjects.

One more number rides along with the score and cannot be taken out. A Russian
university adds up to ten points for individual achievements — a gold medal, a
sports rank, a school essay — and the monitoring subtracts them only where the
admission list shows them. In 2025 it could not for 95 universities holding
41,407 budget places, a twelfth of the total, and their averages carry those
points. `id_deducted` marks which rows those are.

## Placing a score on the cohort

Russia publishes no national distribution of exam scores in a form a program
can read. FIPI draws it as a picture in each subject report, and Rosobrnadzor,
Rosstat and fedstat all refuse automated requests. What is published is every
admitted group's average and headcount, and the size of the exam cohort.

`cohort.py` walks the groups from the highest average down, accumulating
headcounts, which gives each score the rank it reaches — the same shape as a
Chinese 一分一段 table, built from the admitted side. It walks the field tables
rather than the university ones, which are coarser; that costs the 2% of the
intake sitting in groups too small for a field row. `data/cohort-steps.tsv`
holds the result, `lib/percentile.py` is the only place that reads it, and
every `ability` column in `rankings/` comes through that one function.

The base it divides by is the number of people who sat the compulsory Russian
paper, which `parse/fipi.py` reads out of the FIPI subject report: 655,000 in
2025. `assessment-pool.tsv` carries that number for `compare/`. FIPI's
analytical materials start at 2019, so the years before it are ranked on the
published average alone and their `ability` column is empty.

Two assumptions hold the construction up, and both are visible in
`data/cohort-model.tsv`. They push the ranking in opposite directions.

An admitted student is placed where their group's average is placed. A group
averaging 90 holds students at 84 and at 96, and all of them land on 90, so
the tails flatten and the top of the scale runs short of people. Phystech's
2025 average of 94.4 reads as the 99.80th percentile, the top 1,310 of the
cohort, while its own non-olympiad intake alone puts about 330 students above
that score; every other university's high scorers are hidden inside groups
whose average is lower. The error is a few tenths of a percentile point at the
very top and falls away quickly below it, and it never reorders anything,
because a percentile here is monotone in the score it came from.

Every admitted student is also counted as an exam participant, which the
monitoring's headcount does not promise — it counts admits on a college
diploma and on a university's own test too. In 2011, the one year the
monitoring published the count, 210,572 of the 272,006 budget admits had a
readable exam total, 77% of the headcount. That puts 87% of the 2025 exam
cohort into a full-time first-degree place, too many, and pushes every
percentile down.

The construction makes seats fill the cohort exactly, so there is no
seat-against-candidate check to run here: it would pass by definition.

## Outputs

- `rankings/rank-universities.tsv` and `rankings/rank-fields.tsv`: every
  university and укрупнённая группа, ranked inside its year and route, with the
  published average, the average without olympiad winners, and the percentile.
- `rankings/ability-universities.tsv`: one row per university for the latest
  year, budget and paid places averaged by seat, which is the table `compare/`
  would read.
- `rankings/route_ability.tsv`: the same allocations split by route, with
  olympiad winners as their own route at the top of the scale.
- `rankings/ability-spread.png`: what a university average covers, and how the
  olympiad route concentrates at the top.
- `data/admissions-universities.tsv`, `data/admissions-fields.tsv`: the parsed
  monitoring, 2011–2025.
- `data/ege-national.tsv`: exam participants and the national mean per year.
- `data/cohort-steps.tsv`, `data/cohort-model.tsv`: the percentile walk and
  what it rests on.
- `data/source-coverage.tsv`: what each of the 60 mirrored pages publishes,
  year by year, including columns the ranking does not read.

## Rebuilding

    ./rebuild.sh

Set `PYTHON` to use a different interpreter. `parse/fipi.py` needs Poppler's
`pdftotext`. The commands run separately as well:

    python3 -m fetch.hse            # 60 rating pages, half an hour cold
    python3 -m fetch.fipi           # the compulsory Russian subject reports
    python3 -m parse.hse            # data/admissions-*.tsv
    python3 -m parse.fipi           # data/ege-national.tsv
    python3 coverage.py             # data/source-coverage.tsv
    python3 cohort.py               # the percentile walk and assessment-pool.tsv
    python3 rank.py                 # rankings/rank-*.tsv
    python3 route_ability.py        # rankings/route_ability.tsv
    python3 plot.py                 # rankings/ability-spread.png
    python3 -m unittest discover

`fetch.hse` takes years as arguments and `fetch.fipi` takes subject names, so
one year or one subject can be refreshed alone; `--force` re-downloads what is
already mirrored.
