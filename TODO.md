# TODO

Order: impact first. “Done when” describes a published table, not a download.

## Put the percentile on measured ground — highest impact

- [ ] **Replace the derived step table with a published score distribution.**
  `cohort.py` builds `data/cohort-steps.tsv` out of the admitted groups
  themselves, on the assumption that a student ranks where their group's
  average ranks. That flattens both tails: a group averaging 90 holds students
  at 84 and at 96, and the table puts all of them at 90. FIPI draws the real
  distribution as a picture, and Rosobrnadzor, Rosstat and fedstat all refuse
  automated requests, so the numbers have to come from somewhere else —
  pooled regional statistical reports, an archived Rosobrnadzor release, or a
  mirror. Done when a percentile comes from counted participants.

- [ ] **Spread each group around its average.** Short of a published
  distribution, the walk can put a group's students on a curve instead of on a
  point, which is what the top of the scale needs. The width has to be measured,
  not chosen: the tables through 2016 print the weakest admitted student beside
  the average, and the field tables give the between-group part of the variance
  directly. Watch out that the weakest admit is usually a quota place, so the
  gap overstates the ordinary spread. Done when the width has a source and the
  ranking states how far it moved the top.

- [ ] **Take the non-exam entrants out of the cumulative count.** The
  monitoring counts every admitted student in its headcount but scores only
  those with a computable exam result. Admits on a college diploma, on a
  university's own test, and last year's graduates are all in the denominator
  now, which pushes every percentile down. The size is measurable in one year:
  the 2011 field table publishes both, and 210,572 of 272,006 budget admits had
  a readable total, 77%. Done when `data/cohort-model.tsv` reports scored
  admits separately from total intake for every year.

- [ ] **Weight the cohort base by the subjects a field asks for.** A student
  ranks against everyone who sat Russian, not against everyone who sat the
  three subjects their programme counted. Done when a field's percentile
  states which pool it ranks inside.

- [ ] **Find the exam cohort before 2019.** FIPI's analytical materials start
  at 2019, so `data/ege-national.tsv` does too, and the 2011–2018 rankings
  carry a score with no percentile beside it. Each report quotes the year
  before it, and archived Rosobrnadzor releases cover the rest. Done when every
  ranked year has a participant count with a source.

## Recover what the monitoring already published — modest work

- [ ] **Fix the 2011 and 2012 university tables.** They serve four rows and
  nineteen, with or without a filter query, while their field tables are
  complete — 5,635 groups and 272,006 students in 2011 alone. Roll the field
  table up into a university when the university page is short, or find the
  full page in the archive.

- [ ] **Split the budget route into its quotas.** Целевой приём, особая квота
  and отдельная квота admit on separate competitions at much lower bars. The
  monitoring printed their headcounts through 2017 — in that year 216,545 of
  269,994 budget places went through the general competition, 37,326 through
  целевой приём and 12,103 through особая квота — and has published one blended
  number since. Отдельная квота, another tenth of the places, arrived in 2023
  and has never been visible. 2012–2014 also print the average over the general
  competition alone, which is the score this project actually wants. Done when
  `route_ability.py` names the quota a seat came through for the years that
  publish it, and the general-competition average is ranked where it exists.

- [ ] **Mirror the region tables.** The rating pages filter by субъект РФ, so
  one request per region gives a regional breakdown the national page hides.
  A `Регион` column already survives in 2011 and 2014. Done when every
  university carries a region for every year.

- [ ] **Bound the achievement points that stayed in.** 95 universities and
  41,407 budget places carry `id_deducted = нет` in 2025, so their averages
  include up to ten points the others had taken out. Estimate the size of the
  gap from universities that publish both, and mark the affected rows in the
  ranking rather than only in the parsed table.

- [ ] **Check the averages against FIPI.** `data/ege-national.tsv` holds the
  national mean for the compulsory Russian paper. Extend it to the other
  subject reports and compare the admitted averages against them. Done when
  the gap between the exam mean and the admitted mean has a stated size.

## Reach past the monitoring — narrower payoff

- [ ] **Count the sectors the monitoring never sees.** СПО takes most of the
  ninth-grade cohort and selects on the school certificate, not the ЕГЭ; заочное
  study, master's programmes, and the military, police and arts institutions are
  outside too. None of them has a row anywhere here, so the project cannot say
  what share of an age cohort a university seat represents. Done when each
  excluded sector has an annual intake with a source, or a stated missing-data
  label.

- [ ] **Find seat counts that are not intake counts.** The monitoring reports
  who was admitted, not the контрольные цифры приёма the ministry set. Done
  when a programme's advertised places and its admitted students are separate
  columns.

- [ ] **Rank below the укрупнённая группа.** HSE groups specialities into its
  own broad families, which are coarser than a programme. Done when a table
  names a направление подготовки with its own code.

- [ ] **Add Russia to `compare/`.** It needs `assessment-pool.tsv`, which is
  written, and an age-18 population row. Done when the seventh country appears
  in the shared figures.
