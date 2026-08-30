# TODO

Order: impact first. “Done when” describes a published table, not a download.

## Put the percentile on measured ground — highest impact

- [x] **Replace the derived step table with published score distributions.**
  FIPI supplies 36 subject-year band tables and one digitized full curve.
  `cohort.py` now builds percentiles from those participant distributions.

- [ ] **Spread each group around its average.** Short of a published
  distribution, the walk can put a group's students on a curve instead of on a
  point, which is what the top of the scale needs. The width has to be measured,
  not chosen: the tables through 2016 print the weakest admitted student beside
  the average, and the field tables give the between-group part of the variance
  directly. Watch out that the weakest admit is usually a quota place, so the
  gap overstates the ordinary spread. Done when the width has a source and the
  ranking states how far it moved the top.

- [ ] **Weight the reference by the subjects a field asks for.** The current
  CDF gives every available subject equal weight. Done when an exact program's
  required subjects determine its reference distribution.

- [ ] **Find the exam cohort before 2019.** FIPI's analytical materials start
  at 2019, so `data/ege-national.tsv` does too. Percentiles now carry the
  nearest distribution, but the comparison population still lacks a sourced
  count for 2011–2018.

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

- [ ] **Download the region tables.** The rating pages filter by субъект РФ, so
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

- [ ] **Finish score-gated СПО colleges.** The standardized 2023 monitoring
  pages are now downloaded and parsed into institution GPA indicators and
  offered fields. They omit admitted headcounts and do not cross GPA with
  fields. Find school–programme intake and grade bars, then map them through a
  certificate-grade distribution. Done when the school and major outputs
  include СПО beside university routes with measured seat and ability coverage.

- [ ] **Count the remaining sectors the monitoring never sees.** Part-time
  study, master's programs, and military, police and arts institutions remain
  outside. Done when each sector has an annual intake with a source or a stated
  missing-data label, and every score-gated route is included.

- [ ] **Find seat counts that are not intake counts.** The monitoring reports
  who was admitted, not the контрольные цифры приёма the ministry set. Done
  when a programme's advertised places and its admitted students are separate
  columns.

- [ ] **Rank below the укрупнённая группа.** HSE groups specialities into its
  own broad families, which are coarser than a programme. Done when a table
  names a направление подготовки with its own code.

- [x] **Add Russia to `compare/`.** It needs `assessment-pool.tsv`, which is
  written, and an age-18 population row. Done when the seventh country appears
  in the shared figures.
