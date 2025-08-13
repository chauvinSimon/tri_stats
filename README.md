This document **analyses data** of [**World Triathlon**](https://triathlon.org/), formerly International Triathlon Union (ITU), to **try** to answer questions such as:

- :one_piece_swimsuit: How much faster do elite triathletes **swim when wearing a neoprene wetsuit**? [[link]](#penguin-wetsuit-benefit)
- :penguin: Should **weaker swimmers rejoice** when **wetsuits are allowed**? [[link]](#swimmer-swim-gaps)
- :athletic_shoe: Are runs faster since **carbon plates shoes**? [[link]](#spiral_calendar-level-over-years) 
- :balance_scale: Is the **wetsuit worth for 300m**? [[link]](#is-the-wetsuit-worth-for-300m)
- :three: Does each sport (swim - bike - run) accounts for 1/3 of race durations? What about transitions? [[link]](#question-three-sports)
- :couple: How much faster are **men over women**? In which sport is the gap larger/smaller? How has the gap evolved over the years? [[link]](#couple-women-vs-men)
- :hourglass_flowing_sand: How much faster are athletes in **_sprint_ over _olympic_** distance? [[link]](#stopwatch-paces)
- :chart_with_upwards_trend: Does the level increase **over years**? [[link]](#spiral_calendar-level-over-years)
- :shower: How much time does the **wetsuit add to T1**? [[link]](#shower-wetsuit-at-t1)
- :dart: How often does an athlete **win from a bike breakaway**? [[link]](#dart-race-scenario)
- :runner: How often does the **best runner win**? [[link]](#runner-how-often-does-the-best-runner-win-trophy)
- :rocket: How often is the win decided with a **sprint finish**? [[link]](#rocket-sprint-finish)
- :thermometer: Do **water and air temperatures** affect swimming and running performance? [[link]](#thermometer-temperatures) 
- :white_flag: What are the most represented **nations**? Which nations have serious problems for their **Olympics selection**? [[link]](#earth_africa-athlete-nations)
- :muscle: What is the typical **age** of performing athletes and how has it evolved over years? [[link]](#baby-age)
- :stop_button: **How old** are athletes when they **stop racing** elite short distance triathlon? [[link]](#checkered_flag-age-of-last-race)
- :weight_lifting: What is the **body mass index** of performing triathletes? [[link]](#weight_lifting-body-mass-index)
- :birthday: Are two kids, born the same year but **on two different months**, equally likely to become professional triathletes? [[link]](#date-month-of-birth)

---

# :books: DATA

Data are collected from the [Triathlon.org API](https://developers.triathlon.org/docs/triathlon-api-overview).

> "The **Triathlon.org API Platform** allows access to the entire [Triathlon.org](https://triathlon.org/) infrastructure and data"

**Race results** are processed as followed:
- **Year**: from `2009` (start of the world-series) to mid-`2024`, just after the Paris Olympics.
- **Event**: only **`world-cups`**, **`world-series`** (called **WTCS**) and **`games related events`** (Commonwealth, Olympics and Olympic test events).
- **Distance**: only **`sprint`** (`750 - 20 - 5`) and **`olympic`** (also called "standard": `1500 - 40 - 10`) formats.
- **Minimum number of finishers**: `25`.
- :warning: **IMPORTANT**: How to **summarize** all split-times of one race?
  - For each leg (`swim`, `t1`, `bike`, `t2`, `run`), **an average of `5` times** is computed.
  - Specifically, **the `5`-th to `9`-th best times** in **each sport** are used to compute this average.
  - This **choice is arbitrary** but, as explained below, **relevant for my goal**: _"Analysing the **general competitive field** in **each sport**"._
  - Other settings, e.g. top-1, top-3, top-10 and top-50, could also yield valuable insights, by adjusting a few parameters in the [provided scripts](#computer-code).
  - Notably, the **[PACES](#stopwatch-paces) and [LEVEL OVER THE YEARS](#spiral_calendar-level-over-years) sections** include **top-3 and top-10 analyses** as well. :medal_sports:

---

Why consider **split-times** based on the **ranking in each sport**?
- The split times of the **finish-top-10 athletes** can vary greatly depending on the **race scenario**:
  - For instance, a race might feature a **strong breakaway group of swimmers** reaching T2 with a significant lead, filling the top-10 positions.
  - In the same race, a large pack might arrive at T2 together, with the **strongest runners** then dominating the overall finish.
  - See **[this dedicated section](#dart-race-scenario)** for an **analysis of race scenarios**.
- On the other hand, considering the **ranking in each sport** allows for more **consistent and reliable comparisons** across races.

---

Why consider the **`5`-th to `9`-th best times**?
- To **mitigate outliers**:
  - **Outstanding swimmers, riders, or runners** might **miss a race** due to injury, scheduling conflicts, or other reasons, or they might have **unusually good or bad performances**.
    - Example: In the [2024 World Triathlon Cup Chengdu ( :cn: )](https://triathlon.org/events/event/2024_world_triathlon_cup_chengdu), Therese Feuersinger ( :austria: ) [exited the water](https://youtu.be/WVCUotrmyqY?si=EBgAs7FLYr8uSKxS&t=128) with a **[~50s](https://triathlon.org/results/result/2024_world_triathlon_cup_chengdu/630187) advance**. Considering her swim time, in an e.g. **top-5 average**, is **not appropriate to get a reliable picture of the general level**.
  - Conversely, the `5`-th to `9`-th times are usually denser, providing a **more robust representation** of the **general competitive field**.
- Against **strategic variability** among top performers:
  - The top-4 athletes might engage in **strategic tactics** on the **run**, such as testing each other or waiting for a final sprint, leading to **varying performances**.
    - Similarly, a top athlete may [**slow down** to celebrate a secured win](https://youtu.be/XMa5Soyx498?si=mR0m4P5DcYQFjg87&t=192) or [**push hard** for gold in a close race](https://youtu.be/zTFx6ha7Kos?si=hPv60RpJjL__v9CT&t=7), leading to **significantly different run times**.
  - Conversely, I believe athletes ranked `5`-th to `9`-th are more likely to **give their all without strategic calculations**, resulting in **more robust and consistent comparative times across races**.

---

What about the data quality?
- [World Triathlon](https://triathlon.org) puts efforts to uniform/standardize race reports and race timings.
- But some **manual cleaning** is required.
  - Some information, such as the permission of **wearing wetsuit**, is often missing.
  - Also, I could not find any way to **access the rankings of past years** via the [API](https://developers.triathlon.org/reference/ranking-detail).
- Obviously, **variations in distances**, weather conditions, athlete levels and scenarios make **comparisons between race difficult**.
  - Fortunately, the **number of races** is large enough to smooth out these variations and provide interesting insights.
- **Comparing swim-times** can be tricky, not just because the **distances vary** between events, but also because the **positions of timing mats** are not consistent.
  - Most mats are placed directly at the **exit of the water**, while others are located at the entrance of transition area, which can be **hundreds of meters further**.
  - Future results should be more consistent: World Triathlon is currently working on **standardising placement** of timing mats for all to be at **swim exit** as well as **T-In**.

# :card_index_dividers: CONTENT

> My favourite sections are marked with :star:.

- **[Three sports?](#question-THREE-SPORTS)**
- **[Paces](#stopwatch-PACES)** :star:
- **[Women vs men](#couple-WOMEN-VS-MEN)** :star:
- **[Swim gaps](#swimmer-SWIM-GAPS)**
- **[Swim wetsuit benefit](#penguin-WETSUIT-BENEFIT)** :star:
- **[Wetsuit at T1](#shower-wetsuit-at-t1)** :star:
- **[Race scenario](#dart-RACE-SCENARIO)**
- **[Sprint finish](#rocket-SPRINT-FINISH)**
- **[Level over years](#spiral_calendar-LEVEL-OVER-YEARS)** :star:
- **[Temperatures](#thermometer-TEMPERATURES)**
- **[Host countries](#earth_africa-HOST-COUNTRIES)**
- **[Season duration](#calendar-SEASON-DURATION)** :star:
- **[Athlete nations](#earth_africa-ATHLETE-NATIONS)** :star:
- **[Age](#baby-AGE)**
- **[Age of last race](#checkered_flag-AGE-OF-LAST-RACE)**
- **[Month of birth](#date-MONTH-OF-BIRTH)** :star:
- **[Body mass index](#weight_lifting-BODY-MASS-INDEX)**
- **[Conclusion](#scroll-CONCLUSION)**
  - **[Ideas](#bulb-IDEAS)**
  - **[Takeaways](#takeout_box-TAKEAWAYS)** :star:

---

# :question: THREE SPORTS

This section:
- Investigates the statement: _"swim, bike and run account each for **one third of the total duration**"_.
- Analyses some transition data: T1 and T2.

|                                          ![sport_proportion.png](res/sport_proportion.png)                                           | 
|:------------------------------------------------------------------------------------------------------------------------------------:| 
| *Proportion of `swim`, `t1`, `bike`, `t2` and `run` in the overall race duration. For `women`/`men` and `sprint`/`olympic` formats.* |

Clearly **not 1/3 + 1/3 + 1/3**!
- During a sprint format, women spend **twice as much time running (run+t1+t2) as they do swimming**.
- Athletes spend more than **three times longer on their bikes** than in the water.
- The proportion of the three sports remains similar between **sprint and olympic** formats.
  - The proportion of transition time is almost halved: **transitions are fixed durations** while the **race time doubles** from sprint to olympic.
- Women spend **less _relative_ time** on the swim but more on the run.
  - This observation is consistent with the [section on "Women vs Men"](#couple-women-vs-men).

Why **1.5+40+10** as a format?
- The format was [allegedly](https://en.wikipedia.org/wiki/Triathlon) introduced by the producers of the **U.S. Triathlon Series (USTS)** ( :us: ) in the **mid-1980s**
- According to [this article by the Bass Lake triathlon](https://www.basslaketri.com/history):
- _"A need was seen to **standardize the distances** and make them more in **sync with each individual sport**. USTS is credited with inventing the distances of the **modern day Olympic distance triathlon**. For the swim, 1500 meters was chosen because it is the **standard** long distance competitive swimming event. For the bike, USTS chose **40 kilometers because it was the standard solo time trial distance** in bike racing. And the choice for the run was the **standard road distance of 10 km**. Note that the distances were **not chosen to be symmetrical** nor were they in direct ratio to Ironman distances."_

**Drafting** is allowed on bike.
- Otherwise, gaps would probably be much larger, and probably the **bike skills would become much more decisive**.
- I could not find **when the drafting was first allowed** on elite races.
  - In the first ITU world championship in [1989 in Avignon ( :fr: )](https://triathlon.org/results/result/1989_avignon_itu_triathlon_world_championships), drafting [seems to be banned](https://youtu.be/RLmuXOGXQSU?t=1756).
  - **Banning drafting** seems nowadays complicated, considering the **density of the swim level**. Individual starts, e.g. every minute or so like during cycling time-trials, would be an option, and would give the **bike** section a **much higher importance**.  

**T1 and T2 represent a tiny part** of the overall racing time, yet they are **crucial**!
- E.g. to catch a good bunch at bike.

Comparing to **other triathlon formats**:
- Gustav Iden won the IRONMAN world championships in 2022 with the following times.
- "00:48:23" (3.8k), "4:11:06" (180k), "2:36:15" (42k), which represents:
  - **10.6%** swim
  - **55.1%** bike
  - **34.3%** run
- I.e. **More run** and **less swim**, which was expected from the distances: 3.8-180-42 compared to 1.5-40-10.

<details>
  <summary>Click to expand - 🐇🐢 <strong>Some of the shortest and longest transitions.</strong></summary>

_(using Men data)_

#### T1

The duration of **T1** depends the **distance between the water and the transition area**, as well as on the **position of the timing mats**.
- E.g. when the swim exit happens on a sand beach (Mooloolaba ( :australia: ) , Huatulco ( :mexico: ), Hy-Vee ( :us: )), **timing mats are rarely placed directly on the sand**, but instead further, close to the transition area.
- Short T1 are often related to **unusually long swim times**: the best swim time 19:14 at Hy-Vee ( :us: ) 2010, and 22 min at Mooloolaba ( :australia: ) 2012!
  - That is **a shame**: in such cases **swim split times are incorrect**!
  - Mooloolaba ( :australia: ) has apparently **corrected** the position of the timing mats: the fastest T1 in 2015 was **01:15** (against **00:13** in 2012).

|  T1   |                                                                                                       EVENT                                                                                                        | DISTANCE |
|:-----:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------:|
| 00:13 |                                     [2012 Mooloolaba ITU Triathlon World Cup ( :australia: )](https://www.triathlon.org/events/event/2012_mooloolaba_itu_triathlon_world_cup)                                      | OLYMPIC  |
| 00:16 |                                         [2010 Huatulco ITU Triathlon World Cup ( :mexico: )](https://www.triathlon.org/events/event/2010_huatulco_itu_triathlon_world_cup)                                         | OLYMPIC  |
| 00:16 |                                             [2009 Hy-Vee ITU Triathlon Elite Cup ( :us: )](https://www.triathlon.org/events/event/2009_hy-vee_itu_triathlon_elite_cup)                                             | OLYMPIC  |
|  ...  |                                                                                                        ...                                                                                                         |   ...    |
| 01:26 |                                             [2017 Madrid ITU Triathlon World Cup ( :es: )](https://www.triathlon.org/events/event/2017_madrid_itu_triathlon_world_cup)                                             | OLYMPIC  |
| 01:33 |                             [2017 ITU World Triathlon Grand Final Rotterdam ( :netherlands: )](https://www.triathlon.org/events/event/2017_itu_world_triathlon_grand_final_rotterdam)                              | OLYMPIC  |
| 01:40 |                             [2023 World Triathlon Championship Series Montreal ( :canada: )](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_montreal)                             |  SPRINT  |
| 02:35 |                                         [2011 Guatape ITU Triathlon World Cup ( :colombia: )](https://www.triathlon.org/events/event/2011_guatape_itu_triathlon_world_cup)                                         |  SPRINT  |

#### T2

The duration of T2 is mainly related to the **size of the transition area** (impacted by the number of participants) and to the position of the timing mats.
- Variations are smaller than for T1.

|  T2   |                                                                    EVENT                                                                    | DISTANCE |
|:-----:|:-------------------------------------------------------------------------------------------------------------------------------------------:|:--------:|
| 00:14 |  [2011 Mooloolaba ITU Triathlon World Cup ( :australia: )](https://www.triathlon.org/events/event/2011_mooloolaba_itu_triathlon_world_cup)  | OLYMPIC  |
| 00:14 |  [2012 Mooloolaba ITU Triathlon World Cup ( :australia: )](https://www.triathlon.org/events/event/2012_mooloolaba_itu_triathlon_world_cup)  | OLYMPIC  |
| 00:15 |    [2010 Monterrey ITU Triathlon World Cup ( :mexico: )](https://www.triathlon.org/events/event/2010_monterrey_itu_triathlon_world_cup)     | OLYMPIC  |
|  ...  |                                                                     ...                                                                     |   ...    |
| 00:35 |       [2019 Banyoles ITU Triathlon World Cup ( :es: )](https://www.triathlon.org/events/event/2019_banyoles_itu_triathlon_world_cup)        |  SPRINT  |
| 00:36 |     [2016 Montreal ITU Triathlon World Cup ( :canada: )](https://www.triathlon.org/events/event/2016_montreal_itu_triathlon_world_cup)      |  SPRINT  |
| 00:36 | [2013 Tiszaujvaros ITU Triathlon World Cup ( :hungary: )](https://www.triathlon.org/events/event/2013_tiszaujvaros_itu_triathlon_world_cup) |  SPRINT  |
| 00:41 |      [2017 Salinas ITU Triathlon World Cup ( :ecuador: )](https://www.triathlon.org/events/event/2017_salinas_itu_triathlon_world_cup)      |  SPRINT  |

#### T1+T2

On average, T1+T2 takes **01:11** (men) and **01:18** (women).
- As mentioned for T1, **very short times** are mainly due to **wrong positions of the timing mats after the swim**: they are placed at the entrance of the transition area **instead of at the water exit**.
- Longer T1+T2 means athletes must **run more distance** to reach their bikes / shoes.
  - In Montreal ( :canada: ) 2023, it was 02:13: **more than one minute than usual**.
  - For a sprint format, this is **substantial**: compared to the 15:05 average men's 5k, this long transition makes the **run 7% longer**!

| T1+T2 |                                                                                                       EVENT                                                                                                        | DISTANCE |
|:-----:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------:|
| 00:26 |                                           [2011 Ishigaki ITU Triathlon World Cup ( :jp: )](https://www.triathlon.org/events/event/2011_ishigaki_itu_triathlon_world_cup)                                           | OLYMPIC  |
| 00:27 |                                     [2012 Mooloolaba ITU Triathlon World Cup ( :australia: )](https://www.triathlon.org/events/event/2012_mooloolaba_itu_triathlon_world_cup)                                      | OLYMPIC  |
| 00:28 |                                          [2010 Tongyeong ITU Triathlon World Cup ( :kr: )](https://www.triathlon.org/events/event/2010_tongyeong_itu_triathlon_world_cup)                                          | OLYMPIC  |
| 00:31 |                                     [2010 Mooloolaba ITU Triathlon World Cup ( :australia: )](https://www.triathlon.org/events/event/2010_mooloolaba_itu_triathlon_world_cup)                                      | OLYMPIC  |
|  ...  |                                                                                                        ...                                                                                                         |   ...    |
| 01:48 |                                            [2014 ITU World Triathlon Stockholm ( :sweden: )](https://www.triathlon.org/events/event/2014_itu_world_triathlon_stockholm)                                            |  SPRINT  |
| 01:56 |                             [2017 ITU World Triathlon Grand Final Rotterdam ( :netherlands: )](https://www.triathlon.org/events/event/2017_itu_world_triathlon_grand_final_rotterdam)                              | OLYMPIC  |
| 02:13 |                             [2023 World Triathlon Championship Series Montreal ( :canada: )](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_montreal)                             |  SPRINT  |
| 02:57 |                                         [2011 Guatape ITU Triathlon World Cup ( :colombia: )](https://www.triathlon.org/events/event/2011_guatape_itu_triathlon_world_cup)                                         |  SPRINT  |


</details>

---

---

# :stopwatch: PACES

It is worth recalling the [data](#books-data) settings:

- Year: from `2009` to mid-`2024`.
- Event: only **`world-cups`**, **`world-series`** (called **WTCS**) and **`games related events`**.
- Distance: only **`sprint`** and **`olympic`** formats.
- At least `25` finishers.
- :warning: **IMPORTANT:** for each leg of a race (`swim`, `bike`, `run`), **an average of `5` times** is computed, using the **`5`-th to `9`-th best times of the leg**.

| ![sports_paces.png](res/sports_paces.png) | 
|:-----------------------------------------:| 
|    *Distributions of times and paces.*    |

Note: The distribution of swim times includes races both **with- and without wetsuit**. A [subsequent section](#penguin-wetsuit-benefit) does the distinction (see its _"second method"_ subsection).

<details>
  <summary>Click to expand - 🏅 <strong>Same plots for the Top-3.</strong></summary>

|  ![sports_paces_top3.png](res/sports_paces_top3.png)  | 
|:-----------------------------------------------------:| 
| *Times and paces, considering the Top-3 in each leg.* |

</details>

<details>
  <summary>Click to expand - 🏁 <strong>Same plots for the Top-10.</strong></summary>

| ![sports_paces_top10.png](res/sports_paces_top10.png)  | 
|:------------------------------------------------------:| 
| *Times and paces, considering the Top-10 in each leg.* |

</details>

<details>
  <summary>Click to expand - ⏱️ <strong>Pace/speed/5k/10k conversion for the run.</strong></summary>

| Run Pace (M:SS) | Speed (km/h) | 5k Time (MM:SS) | 10k Time (MM:SS) |
|:---------------:|:------------:|:---------------:|:----------------:|
|      2:55       |     20.6     |      14:35      |      29:10       |
|      2:56       |     20.5     |      14:40      |      29:20       |
|      2:57       |     20.3     |      14:45      |      29:30       |
|      2:58       |     20.2     |      14:50      |      29:40       |
|      2:59       |     20.1     |      14:55      |      29:50       |
|      3:00       |     20.0     |      15:00      |      30:00       |
|      3:01       |     19.9     |      15:05      |      30:10       |
|      3:02       |     19.8     |      15:10      |      30:20       |
|      3:03       |     19.7     |      15:15      |      30:30       |
|      3:04       |     19.6     |      15:20      |      30:40       |
|      3:05       |     19.5     |      15:25      |      30:50       |
|      3:06       |     19.4     |      15:30      |      31:00       |
|      3:07       |     19.3     |      15:35      |      31:10       |
|      3:08       |     19.1     |      15:40      |      31:20       |
|      3:09       |     19.0     |      15:45      |      31:30       |
|      3:10       |     18.9     |      15:50      |      31:40       |
|      3:11       |     18.8     |      15:55      |      31:50       |
|      3:12       |     18.8     |      16:00      |      32:00       |
|      3:13       |     18.7     |      16:05      |      32:10       |
|      3:14       |     18.6     |      16:10      |      32:20       |
|      3:15       |     18.5     |      16:15      |      32:30       |
|      3:16       |     18.4     |      16:20      |      32:40       |
|      3:17       |     18.3     |      16:25      |      32:50       |
|      3:18       |     18.2     |      16:30      |      33:00       |
|      3:19       |     18.1     |      16:35      |      33:10       |
|      3:20       |     18.0     |      16:40      |      33:20       |
|      3:21       |     17.9     |      16:45      |      33:30       |
|      3:22       |     17.8     |      16:50      |      33:40       |
|      3:23       |     17.7     |      16:55      |      33:50       |
|      3:24       |     17.6     |      17:00      |      34:00       |
|      3:25       |     17.6     |      17:05      |      34:10       |
|      3:26       |     17.5     |      17:10      |      34:20       |
|      3:27       |     17.4     |      17:15      |      34:30       |
|      3:28       |     17.3     |      17:20      |      34:40       |
|      3:29       |     17.2     |      17:25      |      34:50       |
|      3:30       |     17.1     |      17:30      |      35:00       |
|      3:31       |     17.1     |      17:35      |      35:10       |
|      3:32       |     17.0     |      17:40      |      35:20       |
|      3:33       |     16.9     |      17:45      |      35:30       |
|      3:34       |     16.8     |      17:50      |      35:40       |
|      3:35       |     16.7     |      17:55      |      35:50       |
|      3:36       |     16.7     |      18:00      |      36:00       |
|      3:37       |     16.6     |      18:05      |      36:10       |
|      3:38       |     16.5     |      18:10      |      36:20       |
|      3:39       |     16.4     |      18:15      |      36:30       |
|      3:40       |     16.4     |      18:20      |      36:40       |

</details>

---

Some **outliers** have been **excluded**:
- :swimmer: from [2012 Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2012_mooloolaba_itu_triathlon_world_cup): see the previous section on [T1](#T1).
- :bicyclist: from [2022 Pontevedra ( :es: )](https://www.triathlon.org/events/event/2022_world_triathlon_cup_pontevedra) and [2024 Hong Kong ( :hong_kong: )](https://www.triathlon.org/events/event/2024_world_triathlon_cup_hong_kong).
- :runner: from [2011 Huatulco, Santa Cruz Bay ( :mexico: )](https://www.triathlon.org/events/event/2011_huatulco_itu_triathlon_world_cup), [2014 New Plymouth ( :new_zealand: )](https://www.triathlon.org/events/event/2014_new_plymouth_itu_triathlon_world_cup), [2014 Tongyeong ( :kr: )](https://www.triathlon.org/events/event/2014_tongyeong_itu_triathlon_world_cup), [2017 Madrid ( :es: )](https://www.triathlon.org/events/event/2017_madrid_itu_triathlon_world_cup) and [2021 Huatulco ( :mexico: )](https://www.triathlon.org/events/event/2021_huatulco_triathlon_world_cup).

---

**Sprint vs olympic** format:
- :swimmer: Swim **paces are almost identical** for 750m and 1500m: about **1s / 100m** difference.
- :bicyclist: There is **less than 1km/h difference** between the 20k and 40k bike.
- :runner: The 10k run requires **7s/km more** than the 5k.

The next section analyses the time differences between **women's and men's** performance.

---

---

# :couple: WOMEN VS MEN

The difference in percent is computed with:

```
diff_in_percent = (time_w - time_m) / time_m

I.e.
time_w = (1 + diff_in_percent) * time_m
```

This percentage says **_"by how much are women slower than men"_**.
- To know _"by how much are men faster"_, use `diff_in_percent / (1 + diff_in_percent)`.  

|      ![wm.png](res/wm.png)      | 
|:-------------------------------:| 
| *By how much are women slower?* |

Notes about **swim data**:
- For fairness, the only **data with identical equipment** (wetsuit or not) for women and men is considered. 
- Some outliers have been removed - can it be due to the **swim being in an ocean/sea? :ocean:**:
  - **25%** at [2022 World Triathlon Cup Miyazaki ( :jp: )](https://www.triathlon.org/events/event/2022_world_triathlon_cup_miyazaki) (sprint): 5th women and men in resp. [`11:03`](https://triathlon.org/results/result/2022_world_triathlon_cup_miyazaki/550760) and [`08:47`](https://www.triathlon.org/results/result/2022_world_triathlon_cup_miyazaki/550759).
  - **27%** at [2023 World Triathlon Cup Valencia ( :es: )](https://www.triathlon.org/events/event/2023_world_triathlon_cup_valencia) (olympic): 5th women and men in resp. [`22:18`](https://triathlon.org/results/result/2023_world_triathlon_cup_valencia/582219) and [`17:30`](https://www.triathlon.org/results/result/2023_world_triathlon_cup_valencia/582218).
  - **28%** at [2009 Dextro Energy Triathlon - ITU World Championship Grand Final Gold Coast ( :australia: )](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_grand_final_gold_coas) (olympic): Liz Blatchford ( :gb: ) and Javier Gomez ( :es: ) are 5th out of water in resp. [`21:47`](https://www.triathlon.org/results/result/2009_dextro_energy_triathlon_-_itu_world_championship_grand_final_gold_coas/4818) and [`17:02`](https://triathlon.org/results/result/2009_dextro_energy_triathlon_-_itu_world_championship_grand_final_gold_coas/4819).

---

|                                 ![wm_over_years.png](res/wm_over_years.png)                                 | 
|:-----------------------------------------------------------------------------------------------------------:| 
|                            *By how much are women slower? Evolution over years.*                            |

<details>
  <summary>Click to expand - 📈 <strong>Evolution over years, considering only WTCS and games-related events.</strong></summary>

|           ![wm_over_years_no_world_cup.png](res/wm_over_years_no_world_cup.png)           | 
|:-----------------------------------------------------------------------------------------:| 
| *By how much are women slower? Evolution over years. Only WTCS and games-related events.* |

</details>

---

:bulb: **FINDINGS:**
- :swimmer: The **swim** is the sport where the **relative difference** between women and men is the **smallest**.
  - Swimming is highly **technique-oriented**.
  - Women often excel in technical sports because these **rely less on raw strength** and more on skill, coordination, and efficiency.
  - Women and men have **different buoyancy**, as explained by Maria Francesca Piacentini, in [this episode](https://scientifictriathlon.com/tts392/) (at 19:00) of the [triathlon show podcast](https://scientifictriathlon.com/podcast/).
  - As reported by [this 2019 article](https://www.researchgate.net/publication/334664495_Sex_Difference_in_Triathlon_Performance) by Romuald Lepers: _"Elite female athletes generally have **7–12% more body fat** than males (Fleck, 1983; Heydenreich et al., 2017). As fat is buoyant in water, **women are less penalized than men in swimming** than they are within **terrestrial events** such as cycling and running. Male triathletes also possess a **larger muscle mass**, greater **muscular strength** and **lower relative body fat** than female triathletes (Knechtle et al., 2010a)."_
- :runner: The **run** is where the difference is the **largest**.
  - Men typically have **greater muscle mass** and **aerobic capacity**, which can provide an advantage in endurance activities like running.
- :straight_ruler: The **standard deviation** is **higher for swim and lower for run**.
  - Because **swim conditions (wind, current, temperature) can vary** and athletes may follow non-straight swim lines leading to larger swim distances?
- :chart_with_downwards_trend: The **w/m difference has not significantly reduced** on the years, except for the **run leg of the sprint-format races (-0.13 % / year)**.
  - Note: Probably some **data processing should be applied** to the [line fitting](https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html).
    - E.g. to account for the very low number of points during the covid pandemic?
  - In WTCS and games-related events, the **w/m swim gap has reduced (-0.11 % / year)** as well.

These **percentages can be compared** with those of **swim, bike or run competitions**:

<details>
  <summary>Click to expand - 🏊🚴🏃 <strong>Comparisons to individual swim/bike/run.</strong></summary>

**`diff_percent = (time_w - time_m) / time_m`** is computed for a **couple of events** taken individually.
- It would be **statistically more significant** to **consider many events** and compute **averages**.
- I have not taken the time to do that.

:swimmer: **SWIM**
- :jp: **2021 Tokyo 800m: `diff_percent = 7.7%`** considering the 4th to 8th [men](https://olympics.com/en/olympic-games/tokyo-2020/results/swimming/men-s-800m-freestyle) and [women](https://olympics.com/en/olympic-games/tokyo-2020/results/swimming/women-s-800m-freestyle):
  - `times_m = [7:42.68, 7:45.00, 7:45.11, 7:49.14, 7:53.31]`
  - `times_w = [8:19.38, 8:21.93, 8:22.25, 8:24.56, 8:26.30]`
  - In previous olympic games, there was **no men's 800m**.
    - In Rio, the 4th-8th women average was less than 1s different to Tokyo.
- :jp: **2021 Tokyo 10k: `diff_percent = 8.2%`** considering the 5th to 9th [men](https://en.wikipedia.org/wiki/Swimming_at_the_2020_Summer_Olympics_%E2%80%93_Men%27s_marathon_10_kilometre) and [women](https://en.wikipedia.org/wiki/Swimming_at_the_2020_Summer_Olympics_%E2%80%93_Women%27s_marathon_10_kilometre):
  - `times_m = [1:49:29, 1:50:23, 1:51:30, 1:51:32, 1:51:37]`
  - `times_w = [1:59:35, 1:59:36, 1:59:37, 2:00:10, 2:00:57]`
  - **Open-water conditions** are closer to the one of triathlon, but the 10k race involves more strategy.

:bicyclist: **BIKE**
- Which race format?
  - **Non-TT cycling race** often **involve strategy**, making time comparison between women and men irrelevant.
  - ICU time-trial (TT) world championships uses **different distances** for [women](https://en.wikipedia.org/wiki/UCI_Road_World_Championships_%E2%80%93_Women%27s_time_trial) and [men](https://en.wikipedia.org/wiki/UCI_Road_World_Championships_%E2%80%93_Men%27s_time_trial), making the comparison difficult.
  - Fortunately **regional and national TT championships** use the same distance and can therefore give **relevant examples of `diff_percent`**.
- :us: **2024 USA TT: `diff_percent = 11.1 %`** between Taylor Knibb ([`41:54`](https://my.raceresult.com/290103/#2_45D764)) and Brandon McNulty ([`37:42`](https://my.raceresult.com/290103/#4_B2D212))
- :eu: **2023 European TT: `diff_percent = 12.3%`** considering the 5th to 9th [men](https://en.wikipedia.org/wiki/2023_European_Road_Championships_%E2%80%93_Men%27s_time_trial) and [women](https://en.wikipedia.org/wiki/2023_European_Road_Championships_%E2%80%93_Women%27s_time_trial):
  - `times_m = [32:43.77, 32:45.91, 32:52.03, 32:55.19, 32:55.22]`
  - `times_w = [36:42.01, 36:49.02, 36:53.75, 37:02.27, 37:05.13]`
- :eu: **2022 European TT: `diff_percent = 14.8%`** considering the 5th to 9th [men](https://en.wikipedia.org/wiki/2022_European_Road_Championships_%E2%80%93_Men%27s_time_trial) and [women](https://en.wikipedia.org/wiki/2022_European_Road_Championships_%E2%80%93_Women%27s_time_trial):
  - `times_m = [27:42.81, 28:01.56, 28:17.61, 28:18.47, 28:27.19]`
  - `times_w = [32:00.87, 32:01.10, 32:30.76, 32:32.76, 32:37.85]`

:running: **RUN**
- `diff_percent` is computed in the same way.
  - But keep in mind that running competitions are **often very strategic**: the time matters often less than the ranking.
    - For instance, on the athletic track the **pace can be kept low until the last lap**.
  - **Comparing world/continental/national records** for women vs men is an option, but the level of one outstanding person says nothing about the **average level**.
- :eu: **2024 European 10k: `diff_percent = 13.8%`** considering the 5th to 9th [men](https://en.wikipedia.org/wiki/2024_European_Athletics_Championships_%E2%80%93_Men%27s_10,000_metres) and [women](https://en.wikipedia.org/wiki/2024_European_Athletics_Championships_%E2%80%93_Women%27s_10,000_metres):
  - `times_m = [31:34.90, 31:38.45, 32:15.91, 32:16.85, 32:17.24]`
  - `times_w = [28:01.42, 28:04.43, 28:09.87, 28:10.97, 28:11.61]`
- :eu: **2024 European 5k: `diff_percent = 11.6%`** considering the 5th to 9th [men](https://en.wikipedia.org/wiki/2024_European_Athletics_Championships_%E2%80%93_Men%27s_5000_metres) and [women](https://en.wikipedia.org/wiki/2024_European_Athletics_Championships_%E2%80%93_Women%27s_5000_metres):
  - `times_m = [14:44.72, 14:58.28, 15:00.05, 15:02.56, 15:05.66]`
  - `times_w = [13:23.26, 13:24.54, 13:24.80, 13:25.08, 13:25.65]`
- :fr: **2024 Paris marathon: `diff_percent = 13.7%`** considering the 5th to 9th [men](https://worldathletics.org/competition/calendar-results/results/7208360) and [women](https://worldathletics.org/competition/calendar-results/results/7208360?eventId=10229534&gender=W):
  - `times_m = [2:24:48, 2:26:00, 2:26:01, 2:26:03, 2:26:08]`
  - `times_w = [2:07:37, 2:07:39, 2:07:44, 2:08:41, 2:09:04]`

</details>

---

#### Focus on the swim: :swimmer:

|                             ![wm_swim.png](res/wm_swim.png)                             | 
|:---------------------------------------------------------------------------------------:| 
| *By how much swim women slower, with / without wetsuit? :swimmer: :one_piece_swimsuit:* |

:bulb: **FINDING**:
- The **women/men time difference** can be considered **constant**, **regardless of the distance** (sprint / olympic) and **the equipment** (wetsuit or not): **women swim ~8.8% slower**.
- This finding is consistent with [Vleck et al., 2011](https://www.triathlon.org/uploads/docs/Proceedings_I_World_Conference_of_Science_in_Triathlon.pdf).
- This result will be used in a [subsequent section](#penguin-wetsuit-benefit) to determine the **benefit provided by the wetsuit**.

---

---

# :swimmer: SWIM GAPS

This section tries to answer the question **_"Should worse swimmers be happy when the wetsuit is allowed?"_**.
- My **_a priori_ reflexion** was:
  - The wetsuit makes everyone swim faster.
  - => The **swim takes less time**.
  - => => **Gaps are smaller**.
  - => => => **Worse swimmers are happy**.

Approach:
- For each race, the gap between the **5-9th first swimmers** and **5-9th last swimmers** is computed.
- These **gaps are split into two groups**: `with-wetsuit` and `without-wetsuit`.
- The **averages of both group** are compared to determine **if the wetsuit makes swim gaps smaller or larger**. 

|                          ![swim_gaps.png](res/swim_gaps.png)                           | 
|:--------------------------------------------------------------------------------------:| 
| *Comparing **average gaps between good and "bad" swimmers** with and without wetsuit.* |

:bulb: **FINDINGS**:
- **Variations in the swim-pack length** between **event with-wetsuit and without-wetsuit** are **very small**.
- There is **no evidence** that worse swimmers should be happy about the wetsuit.
  - The **wetsuit even tends to stretch the swim pack**, especially for women. 
  - To be honest, I would have **expected the opposite!**

**POSSIBLE INTERPRETATION #1**:
- Wetsuits are typically worn in **cold waters**, often in **seas and oceans**, where waves can make swimming more challenging, potentially spreading out the pack.
- However, there are many examples of sea and ocean swims that occur without wetsuits!
- Therefore, I would **dismiss this hypothesis**.

**POSSIBLE INTERPRETATION #2**:
- True, the **swim is shorter in time**.
- But gaps **do not significantly reduce** because the **benefit provided by the wetsuit differs** between good and worse swimmers:
  - For **5-9th** top swimmer: **5.4%**.
  - For **20-24th** top swimmer: **5.3%**.
  - For last **9-5th** top swimmer: **4.9%**.
  - More details on this derivation can be found in the [dedicated section](#penguin-wetsuit-benefit).
- In other words, despite the shorter swim duration, **gaps do not reduce** because **top swimmers gain more benefits** from the wetsuit.

**QUESTION**:
- Would the wetsuit enable the **slowest swimmers** (last 9-5th) to **catch the good swimmers** (first 5-9th)?
  - On the olympic format, the **gap is about 56s and 49s** without wetsuit, while the fast women and men swim [on average in 19:30 and 17:57](#stopwatch-paces).
  - A **4.9% improvement** for the slowest swimmers represent `0.049 * (19:30 + 0:56) =` **60s**, and  `0.049 * (17:57 + 0:49) =` **55s**.
  - Conclusion: the slowest swimmers with the **benefit of the wetsuit** would be **~10s faster that the good swimmers** without.

<details>
  <summary>Click to expand - <strong>Other comparisons.</strong></summary>

---

Considering the **"front-to-middle" distance** (using the **20-24th** swimming times instead of the last 5-9th), results looks similar: **No significant gap reduction**.
- `men`+`sprint`+`no_wetsuit` may suffer from outliers: gaps at Tiszaújváros ( :hungary: ) 2013 and 2016 were larger than 33s.

|                     ![swim_gaps_20-24.png](res/swim_gaps_20-24.png)                     | 
|:---------------------------------------------------------------------------------------:| 
| *Same computation as above, this time with gaps between 5-9th to **20-24th** swimmers.* |

---

When considering **world-series events only**, the opposite trend occurs: the **wetsuit tends to reduce the swim gaps**.
- However, as noted earlier, **variations are very small**, indicating that **no significant effect of the wetsuit on swim gaps can be concluded**.

| ![swim_gaps-wcs.png](res/swim_gaps-wcs.png) | 
|:-------------------------------------------:| 
|      *With world-series events only.*       |

</details>

---

---

# :penguin: WETSUIT BENEFIT

This section tries to **estimate the benefit (in percent) offered by the wetsuit**, defined as

```
improve_percent = (time_no_wetsuit - time_wetsuit) / time_no_wetsuit

I.e.
time_with_wetsuit = (1 - improve_percent) * time_without_wetsuit
```

Main challenge:
- **Only one of [`time_no_wetsuit`, `time_wetsuit`]** is typically available: the one recorded during the race.
- This sections introduces different methods to **estimate the missing `time_`**, enabling the calculation of `improve_percent`.

Reminder:
- The scope here is **elite triathletes**, going **5-9th** out of water on top World Triathlon events.
- Results would certainly **differ for beginners** and hobby triathletes.

---

### :couple: Method 1: using **women/men differences**

The idea of the **derivation** is as follows:
- **Women [have been found](#focus-on-the-swim-swimmer) to swim on average ~8.8% slower than men**, with the **same equipment**.
- With examples where **women had the wetsuit**, but **men did not**, one can:
  - 1- Estimate, from the men's time, the **time women WOULD HAVE done without the wetsuit** (thanks to the ~8.8% rule).
  - 2- Compare the **women's time with wetsuit** (measured) with the **women's time without** (computed in 1-).
  - 3- Deduce the **advantage provided by the wetsuit** for the women.
  - 4- Note that `improve_percent` should be the **same for women and men** (because of the **constant** ~8.8% difference given the **same equipment**).

- Advantages of this method:
  - **Proper environment**: data comes from **real races**, as opposed to studies in 50m or even 25m pools.
  - **No need to know the exact swim distance**: what matters is that men and women swim the **exact same course**. This assumption is **reasonable** because the buoys should not move between the two races.
  - **Data-based**: the 8.8% should be **robust** since it leverages results from many races (230 events).
  - **Low cost**: all the data is available online for free.

- Limitations:
  - The **swim conditions** are not guaranteed to be equal.
    - For instance in [Cagliari ( :it: ) 2024](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_cagliari) the **seawater** was [more **choppy** :ocean: for the men](https://youtu.be/-Su5kpPz0hY?t=79) than [for the women](https://youtu.be/vFV-kB8727I&t=69s).
    - This might explain why the gap between men and women was slightly smaller than average.
  - The **limited number of events** where the "women-with / men-without" scenario occurs.
    - Only five races fit this scenario, but the **variability is low**: `std = 0.5%`.

<details>
  <summary>Click to expand - ✏️ <strong>Derivation of the formula.</strong></summary>

```
# VARIABLES
  swim_w:             time of women. no wetsuit.
  swim_m:             time of men. no wetsuit.
  swim_w_wet:         time of women. with wetsuit.
  
  improve_percent:    advantate (in percent) brought by the wetsuit. UNKNOWN.
  wm_percent:         relative delay of women over men assuming same equipment.
  wm_percent_w_fast:  relative delay when women have wetsuit, but men do not.

# FORMULA
  would W have not had wetsuit:
    (1)  `swim_w * (1 - improve_percent) = swim_w_wet`  =>  `swim_w = swim_w_wet / (1 - improve_percent)` 
  and this time would be related to swim_m:
    (2)  `swim_w = swim_m * (1 + wm_percent)`
  using (1) == (2):
    (3)  `swim_w_wet = swim_m * (1 + wm_percent) * (1 - improve_percent)`
  
  on the other hand:
    (4)  `swim_w_wet = swim_m * (1 + wm_percent_w_fast)`
  
  using (4) == (3):
    (5)  `(1 + wm_percent) * (1 - improve_percent) = (1 + wm_percent_w_fast)`
  re-written:
         `(1 - improve_percent) = (1 + wm_percent_w_fast) / (1 + wm_percent)`
  hence
         `improve_percent = 1 - (1 + wm_percent_w_fast) / (1 + wm_percent)`

# EXAMPLE
  [wm_percent = 8.8%]
  [wm_percent_w_fast = 2.9%]
  => improve_percent = 1 - (1+0.029)/(1+0.088) = 5.4%

```

</details>

|                                        ![wetsuit.png](res/wetsuit.png)                                         | 
|:--------------------------------------------------------------------------------------------------------------:| 
| *Estimating the benefit brought by the wetsuit, using results of races where women swam with but men without.* |

:bulb: **FINDING**:
- The **wetsuit brings an advantage of ~5.4%** to top swimmers (5th-9th).
- Put differently, top swimmers (top 5-9) swim **~5.7% slower without wetsuit**.
  - `0.054 / (1-0.054) = 0.057`.

:warning: **CRITICISMS AND IDEAS FOR IMPROVEMENT**:
- **1) Uncertainty**:
  - How to **account for uncertainties** in `wm_percent_w_fast` and `wm_percent` in the `improve_percent = 1 - (1 + wm_percent_w_fast) / (1 + wm_percent)` formula?
    - So far, the [**standard deviations**](https://en.wikipedia.org/wiki/Standard_deviation) were computed (`± 3.0%` and `± 0.5%`), telling **how spread out** the observed w/m-swim-diff percentages are:
      - `wm_percent = 8.8% ± 3.0%`.
      - `wm_percent_w_fast = 2.9% ± 0.5%`.
      - Concretely, in the case of `wm_percent`, `± 3.0%` [can be interpreted](https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule) as: _"~68% of the observed w/m-swim-diff percentages lie between 8.8%-3% and 8.8%+3%"._
    - I am not sure, but from what I understood, in order to produce a **confidence interval** for `improve_percent`, the **[standard errors](https://en.wikipedia.org/wiki/Standard_error) (`SE`)** should be used instead:
      - `SE(wm_percent) = 3.0% / sqrt(230) = 0.2%`.
      - `SE(wm_percent_w_fast) = 0.5% / sqrt(5) = 0.2%`.
  - In statistics, this question is known as [Propagation of Uncertainty](https://en.wikipedia.org/wiki/Propagation_of_uncertainty).
    - Approach #1 (simple): perform calculations using the extremes of the error intervals to see where `improve_percent` falls.
      - Here, applying the combinations (-0.2%, -0.2%), (-0.2%, +0.2%), (+0.2%, -0.2%) and (+0.2%, +0.2%) to (`wm_percent = 8.8%`, `wm_percent_w_fast = 2.9%`).
      - This results in the interval **`improve_percent = 5.4%` with `0.4%` standard error**.
    - Approach #2 (using [partial derivatives](https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Simplification)):
      - Using [this tool](https://statpages.info/erpropgt.html), I obtain **`improve_percent = 5.4%` with `0.3%` standard error**.
- **2) Events consistency**:
  - `wm_percent_w_fast = 2.9%` was computed from **five** _"women-with-wetsuit, men-without"_ examples that **all have the following properties**: **WTCS** and **olympic-format**.
    - The five **venues** are: Yokohama ( :jp: ) (twice), Cagliari ( :it: ), Stockholm ( :sweden: ) and Edmonton ( :canada: ).
  - In contrast, `wm_percent = 8.8%` was obtained by considering **all** the sprint- and olympic-format WCTS, world-cups and games-related events since 2009, totaling **220 events**.
    - This is inconsistent.
  - Instead, `wm_percent` should be estimated considering events with **similar swim conditions** as those for `wm_percent_w_fast`.
    - Idea #1: Only consider events with the **same event-category** (WTCS), and possibly the **same format** (olympic). For comparison:
      - :warning: WTCS-only: **`improve_percent=4.8%`**, with a lower women/men difference (8.1%).
      - :warning: World-cups-only: **`improve_percent=4.0%`**, with a higher women/men difference (9.4%).
    - Idea #2: Further restrict Idea #1 (same format and event-category), by considering only with the **same venues**.
      - The four venues mentioned have **hosted multiple** olympic-WTCS: 20 times, from which **15** had women and men sharing the same equipment for the swim.
      - This gives `wm_percent = 7.4% ± 1.6%` (`SE = 1.6/sqrt(15) = 0.4%`), leading to **`improve_percent = 4.2%` with `0.3%` standard error**.
    - **IMPORTANT CONCLUSION:**
      - There is a **trade-off between data-quantity and data-quality**.
      - :arrow_right: First refinements suggest wetsuit improvements **closer to 4-5%**. :arrow_left:
- **3) Additional examples**:
  - Several **other events** feature the _"women-with / men-without"_ scenario.
    - Tongyeong ( :kr: ) ([2011](https://www.triathlon.org/events/event/2011_tongyeong_itu_triathlon_world_cup), [2014](https://www.triathlon.org/events/event/2014_tongyeong_itu_triathlon_world_cup), [2016](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup)), [Arzachena ( :it: ) (2020)](https://www.triathlon.org/events/event/2020_arzachena_itu_triathlon_world_cup), [Haeundae ( :kr: ) (2021)](https://www.triathlon.org/events/event/2021_world_triathlon_cup_haeundae) are **world-cups** events, so they have not been included.
    - [Sydney ( :australia: ) (2012)](https://www.triathlon.org/events/event/2012_itu_world_triathlon_sydney),  despite being a WTCS, was excluded due to an **unusual w/m swim difference**: women swam 10.1% slower than men, even with the wetsuit advantage.
  - It would be valuable to include events with the **opposite scenario**: _"women-without / men-with"_.
    - I have found only one: [New Plymouth ( :new_zealand: ) 2017](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup).
  - Future events may **provide additional examples** to further refine the estimate.
- **4) Function approximation**:
  - Currently, the **relationship between `swim_w` and `swim_m`** is **modelled as linear**: `swim_w = swim_m * (1 + wm_percent)`.
    - Could this relationship be better captured using **more sophisticated models**, such as neural networks?
    - _What additional inputs might enhance prediction accuracy? For example, should the model consider the complete list of swim times?_

<details>
  <summary>Click to expand - 🌍 <strong>Events used for the derivation.</strong></summary>

|  YEAR  |                                                      EVENT                                                      |  DIFF (%) WOMEN-WITH vs MEN-without  |  **BENEFIT (%)**  |  DISTANCE  |  EVENT CATEGORY  |
|:------:|:---------------------------------------------------------------------------------------------------------------:|:------------------------------------:|:-----------------:|:----------:|:----------------:|
|  2024  |  [Cagliari](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_cagliari) ( :it: )  |                 2.3%                 |     **6.0%**      |  olympic   |       WTCS       |
|  2021  |    [Edmonton](https://www.triathlon.org/events/event/2021_world_triathlon_grand_final_edmonton) ( :canada: )    |                 2.4%                 |     **5.9%**      |  olympic   |       WTCS       |
|  2022  |  [Yokohama](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama) ( :jp: )  |                 2.9%                 |     **5.4%**      |  olympic   |       WTCS       |
|  2015  |       [Stockholm](https://www.triathlon.org/events/event/2015_itu_world_triathlon_stockholm) ( :sweden: )       |                 3.3%                 |     **5.0%**      |  olympic   |       WTCS       |
|  2024  | [Yokohama](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_yokohama1) ( :jp: )  |                 3.5%                 |     **4.9%**      |  olympic   |       WTCS       |

</details>

---

### :earth_africa: Method 2: Using **Recurring Events**

This method identifies **pairs of events** held at the **same venue**, where wetsuits were **required in one year** but **not in another**.
- The approach assumes that the **course layout remains consistent** across years.
- For example, in the men's race at Yokohama ( :jp: ), wetsuits were worn in 2023 (swim time: `17:31`) but not in 2022 (swim time: `18:35`) and not in 2021 (swim time: `18:23`).
- Using these **three events**, **two comparisons** can be made to estimate `improve_percent`:
  - improve_percent = (time_no_wetsuit - time_wetsuit) / time_no_wetsuit
  - **2023 (wetsuit) vs 2021 (no-wetsuit):** `improve_percent = (18:23 - 17:31) / 18:23 = 4.7%`.
  - **2023 (wetsuit) vs 2022 (no-wetsuit):** `improve_percent = (18:35 - 17:31) / 18:35 = 5.7%`.
- By collecting many such comparisons, a **distribution of `improve_percent`** is generated, see the figure below.
- The **mean and median** of this distribution provide an answer to the initial question: **_"How much faster are top swimmers with the wetsuit?"_**

|          ![wetsuit_in_swim_year_to_year.png](res/wetsuit_in_swim_year_to_year.png)          | 
|:-------------------------------------------------------------------------------------------:| 
| *Distribution of the estimated `improve_percent` using the method of **recurring events**.* |

Results from **186 comparisons**:
- **`improve_percent`**:
	- Women+Men  : **`mean = 3.5%`**, **`median = 3.6%`**. (`std = 3.5`)
	- Women only : `mean = 3.6%`, `median = 3.6%`. (`std = 3.2`)
	- Men only   : `mean = 3.4%`, `median = 3.3%`. (`std = 3.7`)
- **Women vs Men**: `0.2%` (with means) or `0.3%` (with medians).

---

:bulb: **DISCUSSION:**
- Challenge: **the swim course varies** across years.
  - The year-to-year comparison incorporates a substantial amount of data (nearly **200 estimates**) and assumes that while some samples may yield **low estimates** and **others high**, the **large dataset size** ensures **these variations balance out**.
    - This approach justifies **including negative estimates**, as the presence of very large benefits is also unlikely.
    - Together, they create a **near-normal distribution**, leading to robust overall estimates.
    - Just to check: _When applied to events using the same swim equipment, the year-to-year comparison yields also a symmetric distribution centered around ~0%, as expected: the swim level does not change, while swim course lengths vary slightly year to year (sometimes longer, sometimes shorter), but remain constant on average._
  - Outliers, however, are addressed by removing estimates **below -5% and above 14%**.
  - To further limit the impact of outliers, comparisons are restricted to **years in close proximity**.
    - The choice of **5 years** as the cutoff is another parameter of the analysis.

<details>
  <summary>Click to expand - ⚖️ <strong>Full list of comparisons used for this derivation.</strong></summary>

Distributions:
- Event category:
	- WTCS      : 73% (135)
	- World-Cup : 27% (51)
- Distance category:
	- Olympic   : 48% (90)
	- Sprint    : 52% (96)

**Venues of the comparisons:**
- 52 (28.0%): Hamburg ( :de: )
- 40 (21.5%): Yokohama ( :jp: )
- 16 ( 8.6%): Edmonton ( :canada: )
- 12 ( 6.5%): New Plymouth ( :new_zealand: )
- 12 ( 6.5%): London ( :gb: )
- 11 ( 5.9%): Tongyeong ( :kr: )
- 10 ( 5.4%): Cagliari ( :it: )
- 10 ( 5.4%): Karlovy Vary ( :czech_republic: )
-  7 ( 3.8%): Auckland ( :new_zealand: )
-  4 ( 2.2%): Cannigione, Arzachena ( :it: )
-  2 ( 1.1%): Valencia ( :es: )
-  2 ( 1.1%): San Diego ( :us: )
-  2 ( 1.1%): Stockholm ( :sweden: )
-  2 ( 1.1%): Montreal ( :canada: )
-  2 ( 1.1%): Sydney ( :australia: )
-  2 ( 1.1%): Chicago ( :us: )

|                                                                EVENT                                                                 |  FORMAT  |  GENDER  |     SWIM WITH WETSUIT      |    SWIM WITHOUT WETSUIT    |  **WETSUIT GAIN (%)**  |
|:------------------------------------------------------------------------------------------------------------------------------------:|:--------:|:--------:|:--------------------------:|:--------------------------:|:----------------------:|
|                  [Cagliari](https://www.triathlon.org/events/event/2017_cagliari_itu_triathlon_world_cup) ( :it: )                   |  SPRINT  |    W     | 10:11 (01:21 /100m) (2019) | 09:47 (01:18 /100m) (2017) |       **-4.0%**        |
|   [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )    | OLYMPIC  |    M     | 17:26 (01:10 /100m) (2011) | 16:46 (01:07 /100m) (2010) |       **-4.0%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2014_tongyeong_itu_triathlon_world_cup) ( :kr: )                  | OLYMPIC  |    M     | 17:08 (01:09 /100m) (2010) | 16:33 (01:06 /100m) (2014) |       **-3.5%**        |
|            [Cagliari](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_cagliari) ( :it: )             | OLYMPIC  |    W     | 19:01 (01:16 /100m) (2024) | 18:23 (01:14 /100m) (2023) |       **-3.4%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2011_tongyeong_itu_triathlon_world_cup) ( :kr: )                  | OLYMPIC  |    M     | 18:12 (01:13 /100m) (2009) | 17:36 (01:10 /100m) (2011) |       **-3.4%**        |
|                  [Cagliari](https://www.triathlon.org/events/event/2018_cagliari_itu_triathlon_world_cup) ( :it: )                   |  SPRINT  |    M     | 09:27 (01:16 /100m) (2019) | 09:13 (01:14 /100m) (2018) |       **-2.5%**        |
|                [Auckland](https://www.triathlon.org/events/event/2015_itu_world_triathlon_auckland) ( :new_zealand: )                | OLYMPIC  |    M     | 18:54 (01:16 /100m) (2011) | 18:28 (01:14 /100m) (2015) |       **-2.3%**        |
|                  [Cagliari](https://www.triathlon.org/events/event/2017_cagliari_itu_triathlon_world_cup) ( :it: )                   |  SPRINT  |    M     | 09:27 (01:16 /100m) (2019) | 09:15 (01:14 /100m) (2017) |       **-2.2%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup) ( :kr: )                  |  SPRINT  |    M     | 09:07 (01:13 /100m) (2018) | 08:55 (01:11 /100m) (2016) |       **-2.2%**        |
|             [Cannigione, Arzachena](https://www.triathlon.org/events/event/2022_world_triathlon_cup_arzachena) ( :it: )              |  SPRINT  |    W     | 09:28 (01:16 /100m) (2020) | 09:17 (01:14 /100m) (2022) |       **-2.0%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    M     | 09:54 (01:19 /100m) (2018) | 09:42 (01:18 /100m) (2019) |       **-2.0%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 19:12 (01:17 /100m) (2015) | 18:50 (01:15 /100m) (2019) |       **-1.9%**        |
|                [Auckland](https://www.triathlon.org/events/event/2014_itu_world_triathlon_auckland) ( :new_zealand: )                | OLYMPIC  |    W     | 20:16 (01:21 /100m) (2011) | 19:55 (01:20 /100m) (2014) |       **-1.7%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:59 (01:12 /100m) (2016) | 08:50 (01:11 /100m) (2013) |       **-1.7%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 18:02 (01:12 /100m) (2015) | 17:45 (01:11 /100m) (2019) |       **-1.7%**        |
|                  [Cagliari](https://www.triathlon.org/events/event/2018_cagliari_itu_triathlon_world_cup) ( :it: )                   |  SPRINT  |    W     | 10:11 (01:21 /100m) (2019) | 10:02 (01:20 /100m) (2018) |       **-1.4%**        |
|   [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )    | OLYMPIC  |    W     | 18:35 (01:14 /100m) (2011) | 18:23 (01:14 /100m) (2010) |       **-1.1%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:43 (01:18 /100m) (2016) | 09:36 (01:17 /100m) (2018) |       **-1.1%**        |
|                [Auckland](https://www.triathlon.org/events/event/2015_itu_world_triathlon_auckland) ( :new_zealand: )                | OLYMPIC  |    W     | 20:16 (01:21 /100m) (2011) | 20:06 (01:20 /100m) (2015) |       **-0.8%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    M     | 08:56 (01:11 /100m) (2019) | 08:52 (01:11 /100m) (2022) |       **-0.8%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:58 (01:16 /100m) (2014) | 18:50 (01:15 /100m) (2019) |       **-0.7%**        |
|                  [Cagliari](https://www.triathlon.org/events/event/2017_cagliari_itu_triathlon_world_cup) ( :it: )                   |  SPRINT  |    W     | 09:51 (01:19 /100m) (2016) | 09:47 (01:18 /100m) (2017) |       **-0.6%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:59 (01:12 /100m) (2016) | 08:56 (01:11 /100m) (2014) |       **-0.4%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:55 (01:16 /100m) (2022) | 18:50 (01:15 /100m) (2019) |       **-0.4%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                  | OLYMPIC  |    W     | 18:50 (01:15 /100m) (2010) | 18:46 (01:15 /100m) (2015) |       **-0.3%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 18:02 (01:12 /100m) (2015) | 17:59 (01:12 /100m) (2012) |       **-0.3%**        |
|                    [Valencia](https://www.triathlon.org/events/event/2022_world_triathlon_cup_valencia) ( :es: )                     |  SPRINT  |    W     | 09:26 (01:15 /100m) (2020) | 09:25 (01:15 /100m) (2022) |       **-0.2%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:59 (01:12 /100m) (2016) | 08:58 (01:12 /100m) (2018) |       **-0.1%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:51 (01:15 /100m) (2018) | 18:50 (01:15 /100m) (2019) |       **-0.0%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:50 (01:11 /100m) (2017) | 08:50 (01:11 /100m) (2013) |        **0.0%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 19:12 (01:17 /100m) (2015) | 19:13 (01:17 /100m) (2017) |        **0.0%**        |
|                  [Cagliari](https://www.triathlon.org/events/event/2018_cagliari_itu_triathlon_world_cup) ( :it: )                   |  SPRINT  |    M     | 09:12 (01:14 /100m) (2016) | 09:13 (01:14 /100m) (2018) |        **0.1%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:56 (01:11 /100m) (2019) | 08:56 (01:11 /100m) (2014) |        **0.1%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                  | OLYMPIC  |    M     | 17:08 (01:09 /100m) (2010) | 17:10 (01:09 /100m) (2015) |        **0.2%**        |
|                [Edmonton](https://www.triathlon.org/events/event/2013_edmonton_itu_triathlon_world_cup) ( :canada: )                 |  SPRINT  |    M     | 08:39 (01:09 /100m) (2016) | 08:40 (01:09 /100m) (2013) |        **0.2%**        |
|                    [Valencia](https://www.triathlon.org/events/event/2022_world_triathlon_cup_valencia) ( :es: )                     |  SPRINT  |    M     | 08:35 (01:09 /100m) (2020) | 08:37 (01:09 /100m) (2022) |        **0.3%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:56 (01:11 /100m) (2019) | 08:58 (01:12 /100m) (2018) |        **0.4%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:43 (01:18 /100m) (2016) | 09:45 (01:18 /100m) (2013) |        **0.4%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    M     | 08:50 (01:11 /100m) (2017) | 08:52 (01:11 /100m) (2022) |        **0.4%**        |
|                  [Cagliari](https://www.triathlon.org/events/event/2017_cagliari_itu_triathlon_world_cup) ( :it: )                   |  SPRINT  |    M     | 09:12 (01:14 /100m) (2016) | 09:15 (01:14 /100m) (2017) |        **0.4%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:43 (01:18 /100m) (2016) | 09:45 (01:18 /100m) (2014) |        **0.5%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    M     | 09:39 (01:17 /100m) (2016) | 09:42 (01:18 /100m) (2019) |        **0.5%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    M     | 08:39 (01:09 /100m) (2016) | 08:43 (01:10 /100m) (2017) |        **0.7%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:42 (01:15 /100m) (2023) | 18:50 (01:15 /100m) (2019) |        **0.7%**        |
|                [Edmonton](https://www.triathlon.org/events/event/2013_edmonton_itu_triathlon_world_cup) ( :canada: )                 |  SPRINT  |    W     | 09:09 (01:13 /100m) (2015) | 09:14 (01:14 /100m) (2013) |        **0.8%**        |
|                [Edmonton](https://www.triathlon.org/events/event/2013_edmonton_itu_triathlon_world_cup) ( :canada: )                 |  SPRINT  |    W     | 09:08 (01:13 /100m) (2016) | 09:14 (01:14 /100m) (2013) |        **1.0%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 17:33 (01:10 /100m) (2014) | 17:45 (01:11 /100m) (2019) |        **1.1%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    M     | 08:39 (01:09 /100m) (2016) | 08:46 (01:10 /100m) (2019) |        **1.3%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:50 (01:11 /100m) (2017) | 08:56 (01:11 /100m) (2014) |        **1.3%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 17:31 (01:10 /100m) (2018) | 17:45 (01:11 /100m) (2019) |        **1.3%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:58 (01:16 /100m) (2014) | 19:13 (01:17 /100m) (2017) |        **1.3%**        |
|                [Edmonton](https://www.triathlon.org/events/event/2013_edmonton_itu_triathlon_world_cup) ( :canada: )                 |  SPRINT  |    M     | 08:33 (01:08 /100m) (2015) | 08:40 (01:09 /100m) (2013) |        **1.4%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:55 (01:16 /100m) (2022) | 19:13 (01:17 /100m) (2017) |        **1.5%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:50 (01:11 /100m) (2017) | 08:58 (01:12 /100m) (2018) |        **1.6%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    M     | 08:56 (01:11 /100m) (2019) | 09:05 (01:13 /100m) (2024) |        **1.6%**        |
|             [Cannigione, Arzachena](https://www.triathlon.org/events/event/2022_world_triathlon_cup_arzachena) ( :it: )              |  SPRINT  |    W     | 09:08 (01:13 /100m) (2021) | 09:17 (01:14 /100m) (2022) |        **1.6%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:43 (01:18 /100m) (2016) | 09:53 (01:19 /100m) (2015) |        **1.7%**        |
|                [Auckland](https://www.triathlon.org/events/event/2014_itu_world_triathlon_auckland) ( :new_zealand: )                | OLYMPIC  |    M     | 17:37 (01:10 /100m) (2012) | 17:57 (01:12 /100m) (2014) |        **1.8%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:40 (01:09 /100m) (2012) | 08:50 (01:11 /100m) (2013) |        **1.8%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    M     | 08:33 (01:08 /100m) (2015) | 08:43 (01:10 /100m) (2017) |        **1.9%**        |
|   [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )    | OLYMPIC  |    M     | 16:27 (01:06 /100m) (2009) | 16:46 (01:07 /100m) (2010) |        **1.9%**        |
|                  [Cagliari](https://www.triathlon.org/events/event/2018_cagliari_itu_triathlon_world_cup) ( :it: )                   |  SPRINT  |    W     | 09:51 (01:19 /100m) (2016) | 10:02 (01:20 /100m) (2018) |        **1.9%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:51 (01:15 /100m) (2018) | 19:13 (01:17 /100m) (2017) |        **1.9%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:59 (01:12 /100m) (2016) | 09:10 (01:13 /100m) (2015) |        **2.0%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:25 (01:15 /100m) (2019) | 09:36 (01:17 /100m) (2018) |        **2.0%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                  | OLYMPIC  |    W     | 18:22 (01:13 /100m) (2011) | 18:46 (01:15 /100m) (2015) |        **2.1%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:24 (01:15 /100m) (2017) | 09:36 (01:17 /100m) (2018) |        **2.2%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 18:02 (01:12 /100m) (2015) | 18:27 (01:14 /100m) (2017) |        **2.2%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    M     | 08:33 (01:08 /100m) (2015) | 08:46 (01:10 /100m) (2019) |        **2.4%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 17:33 (01:10 /100m) (2014) | 17:59 (01:12 /100m) (2012) |        **2.4%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:56 (01:11 /100m) (2019) | 09:10 (01:13 /100m) (2015) |        **2.5%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    W     | 09:09 (01:13 /100m) (2015) | 09:24 (01:15 /100m) (2017) |        **2.5%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:22 (01:15 /100m) (2021) | 09:36 (01:17 /100m) (2018) |        **2.5%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 17:18 (01:09 /100m) (2023) | 17:45 (01:11 /100m) (2019) |        **2.5%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:22 (01:13 /100m) (2024) | 18:50 (01:15 /100m) (2019) |        **2.5%**        |
|            [Yokohama](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_yokohama1) ( :jp: )            | OLYMPIC  |    M     | 17:18 (01:09 /100m) (2023) | 17:45 (01:11 /100m) (2024) |        **2.6%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:29 (01:16 /100m) (2012) | 09:45 (01:18 /100m) (2013) |        **2.7%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2011_tongyeong_itu_triathlon_world_cup) ( :kr: )                  | OLYMPIC  |    M     | 17:08 (01:09 /100m) (2010) | 17:36 (01:10 /100m) (2011) |        **2.7%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    M     | 08:38 (01:09 /100m) (2021) | 08:52 (01:11 /100m) (2022) |        **2.7%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    W     | 09:08 (01:13 /100m) (2016) | 09:24 (01:15 /100m) (2017) |        **2.7%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:29 (01:16 /100m) (2012) | 09:45 (01:18 /100m) (2014) |        **2.7%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 19:12 (01:17 /100m) (2015) | 19:45 (01:19 /100m) (2012) |        **2.8%**        |
|    [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    W     | 18:52 (01:15 /100m) (2012) | 19:25 (01:18 /100m) (2011) |        **2.8%**        |
|    [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    W     | 18:51 (01:15 /100m) (2013) | 19:25 (01:18 /100m) (2011) |        **2.9%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    W     | 09:25 (01:15 /100m) (2019) | 09:42 (01:18 /100m) (2022) |        **3.0%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:40 (01:09 /100m) (2012) | 08:56 (01:11 /100m) (2014) |        **3.1%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    W     | 09:24 (01:15 /100m) (2017) | 09:42 (01:18 /100m) (2022) |        **3.2%**        |
|    [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    W     | 18:52 (01:15 /100m) (2012) | 19:30 (01:18 /100m) (2010) |        **3.2%**        |
|    [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    W     | 18:51 (01:15 /100m) (2013) | 19:30 (01:18 /100m) (2010) |        **3.3%**        |
|             [Cannigione, Arzachena](https://www.triathlon.org/events/event/2022_world_triathlon_cup_arzachena) ( :it: )              |  SPRINT  |    M     | 08:34 (01:09 /100m) (2021) | 08:52 (01:11 /100m) (2022) |        **3.5%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    W     | 09:22 (01:15 /100m) (2021) | 09:42 (01:18 /100m) (2022) |        **3.5%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:25 (01:15 /100m) (2019) | 09:45 (01:18 /100m) (2014) |        **3.6%**        |
|            [Cagliari](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_cagliari) ( :it: )             | OLYMPIC  |    W     | 19:01 (01:16 /100m) (2024) | 19:43 (01:19 /100m) (2022) |        **3.6%**        |
|                   [San Diego](https://www.triathlon.org/events/event/2012_itu_world_triathlon_san_diego) ( :us: )                    | OLYMPIC  |    W     | 17:54 (01:12 /100m) (2013) | 18:34 (01:14 /100m) (2012) |        **3.6%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:24 (01:15 /100m) (2017) | 09:45 (01:18 /100m) (2013) |        **3.6%**        |
|                      [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                       | OLYMPIC  |    M     | 17:31 (01:10 /100m) (2018) | 18:11 (01:13 /100m) (2021) |        **3.6%**        |
|                      [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                       | OLYMPIC  |    W     | 18:55 (01:16 /100m) (2022) | 19:38 (01:19 /100m) (2021) |        **3.6%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:50 (01:11 /100m) (2017) | 09:10 (01:13 /100m) (2015) |        **3.6%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:24 (01:15 /100m) (2017) | 09:45 (01:18 /100m) (2014) |        **3.7%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:38 (01:09 /100m) (2021) | 08:58 (01:12 /100m) (2018) |        **3.8%**        |
|                [Auckland](https://www.triathlon.org/events/event/2014_itu_world_triathlon_auckland) ( :new_zealand: )                | OLYMPIC  |    W     | 19:09 (01:17 /100m) (2012) | 19:55 (01:20 /100m) (2014) |        **3.8%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    W     | 19:05 (01:16 /100m) (2021) | 19:51 (01:19 /100m) (2019) |        **3.8%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    W     | 10:32 (01:24 /100m) (2016) | 10:57 (01:28 /100m) (2019) |        **3.9%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:29 (01:16 /100m) (2012) | 09:53 (01:19 /100m) (2015) |        **3.9%**        |
|  [Yokohama](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: )   | OLYMPIC  |    M     | 18:02 (01:12 /100m) (2015) | 18:47 (01:15 /100m) (2011) |        **4.0%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:58 (01:16 /100m) (2014) | 19:45 (01:19 /100m) (2012) |        **4.0%**        |
|                      [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                       | OLYMPIC  |    W     | 18:51 (01:15 /100m) (2018) | 19:38 (01:19 /100m) (2021) |        **4.0%**        |
|   [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )    | OLYMPIC  |    W     | 17:38 (01:11 /100m) (2009) | 18:23 (01:14 /100m) (2010) |        **4.0%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    M     | 08:30 (01:08 /100m) (2020) | 08:52 (01:11 /100m) (2022) |        **4.2%**        |
|                 [Stockholm](https://www.triathlon.org/events/event/2015_itu_world_triathlon_stockholm) ( :sweden: )                  | OLYMPIC  |    M     | 18:42 (01:15 /100m) (2013) | 19:32 (01:18 /100m) (2015) |        **4.2%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    M     | 08:39 (01:09 /100m) (2016) | 09:02 (01:12 /100m) (2018) |        **4.2%**        |
|    [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    W     | 18:52 (01:15 /100m) (2012) | 19:42 (01:19 /100m) (2009) |        **4.3%**        |
|    [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    W     | 18:51 (01:15 /100m) (2013) | 19:42 (01:19 /100m) (2009) |        **4.3%**        |
|  [Yokohama](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: )   | OLYMPIC  |    W     | 19:12 (01:17 /100m) (2015) | 20:05 (01:20 /100m) (2011) |        **4.4%**        |
|    [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    M     | 17:15 (01:09 /100m) (2013) | 18:02 (01:12 /100m) (2010) |        **4.4%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    W     | 09:09 (01:13 /100m) (2015) | 09:35 (01:17 /100m) (2019) |        **4.5%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup) ( :kr: )                  |  SPRINT  |    M     | 08:31 (01:08 /100m) (2021) | 08:55 (01:11 /100m) (2016) |        **4.6%**        |
|                [Auckland](https://www.triathlon.org/events/event/2015_itu_world_triathlon_auckland) ( :new_zealand: )                | OLYMPIC  |    M     | 17:37 (01:10 /100m) (2012) | 18:28 (01:14 /100m) (2015) |        **4.6%**        |
|    [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    M     | 17:12 (01:09 /100m) (2012) | 18:02 (01:12 /100m) (2010) |        **4.7%**        |
|                [Auckland](https://www.triathlon.org/events/event/2015_itu_world_triathlon_auckland) ( :new_zealand: )                | OLYMPIC  |    W     | 19:09 (01:17 /100m) (2012) | 20:06 (01:20 /100m) (2015) |        **4.7%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    W     | 09:08 (01:13 /100m) (2016) | 09:35 (01:17 /100m) (2019) |        **4.7%**        |
|            [Yokohama](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama) ( :jp: )             | OLYMPIC  |    M     | 17:31 (01:10 /100m) (2018) | 18:23 (01:14 /100m) (2022) |        **4.7%**        |
|                      [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                       | OLYMPIC  |    W     | 18:42 (01:15 /100m) (2023) | 19:38 (01:19 /100m) (2021) |        **4.7%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:25 (01:15 /100m) (2019) | 09:53 (01:19 /100m) (2015) |        **4.8%**        |
|                      [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                       | OLYMPIC  |    M     | 17:18 (01:09 /100m) (2023) | 18:11 (01:13 /100m) (2021) |        **4.9%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:24 (01:15 /100m) (2017) | 09:53 (01:19 /100m) (2015) |        **4.9%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 17:33 (01:10 /100m) (2014) | 18:27 (01:14 /100m) (2017) |        **4.9%**        |
|    [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    M     | 17:15 (01:09 /100m) (2013) | 18:08 (01:13 /100m) (2009) |        **4.9%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    M     | 08:38 (01:09 /100m) (2021) | 09:05 (01:13 /100m) (2024) |        **5.0%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:07 (01:13 /100m) (2020) | 09:36 (01:17 /100m) (2018) |        **5.0%**        |
|    [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    M     | 17:15 (01:09 /100m) (2013) | 18:10 (01:13 /100m) (2011) |        **5.0%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 17:31 (01:10 /100m) (2018) | 18:27 (01:14 /100m) (2017) |        **5.1%**        |
|    [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    M     | 17:12 (01:09 /100m) (2012) | 18:08 (01:13 /100m) (2009) |        **5.2%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    M     | 17:29 (01:10 /100m) (2020) | 18:27 (01:14 /100m) (2019) |        **5.2%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:30 (01:08 /100m) (2020) | 08:58 (01:12 /100m) (2018) |        **5.3%**        |
|    [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )     | OLYMPIC  |    M     | 17:12 (01:09 /100m) (2012) | 18:10 (01:13 /100m) (2011) |        **5.3%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:40 (01:09 /100m) (2012) | 09:10 (01:13 /100m) (2015) |        **5.4%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    M     | 08:33 (01:08 /100m) (2015) | 09:02 (01:12 /100m) (2018) |        **5.4%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    M     | 09:11 (01:13 /100m) (2023) | 09:42 (01:18 /100m) (2019) |        **5.4%**        |
|                  [Montreal](https://www.triathlon.org/events/event/2019_itu_world_triathlon_montreal) ( :canada: )                   |  SPRINT  |    W     | 08:55 (01:11 /100m) (2023) | 09:26 (01:15 /100m) (2019) |        **5.4%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    W     | 18:45 (01:15 /100m) (2020) | 19:51 (01:19 /100m) (2019) |        **5.5%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    W     | 10:32 (01:24 /100m) (2016) | 11:09 (01:29 /100m) (2017) |        **5.5%**        |
|  [Yokohama](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: )   | OLYMPIC  |    W     | 18:58 (01:16 /100m) (2014) | 20:05 (01:20 /100m) (2011) |        **5.6%**        |
|           [Cannigione, Arzachena](https://www.triathlon.org/events/event/2020_arzachena_itu_triathlon_world_cup) ( :it: )            |  SPRINT  |    M     | 08:34 (01:09 /100m) (2021) | 09:04 (01:13 /100m) (2020) |        **5.6%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 19:12 (01:17 /100m) (2015) | 20:23 (01:22 /100m) (2016) |        **5.7%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    W     | 09:25 (01:15 /100m) (2019) | 09:59 (01:20 /100m) (2024) |        **5.8%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    W     | 09:09 (01:13 /100m) (2015) | 09:44 (01:18 /100m) (2018) |        **5.9%**        |
|            [Yokohama](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama) ( :jp: )             | OLYMPIC  |    M     | 17:18 (01:09 /100m) (2023) | 18:23 (01:14 /100m) (2022) |        **5.9%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    W     | 09:07 (01:13 /100m) (2020) | 09:42 (01:18 /100m) (2022) |        **6.0%**        |
|                  [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                   |  SPRINT  |    W     | 09:08 (01:13 /100m) (2016) | 09:44 (01:18 /100m) (2018) |        **6.1%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    W     | 10:17 (01:22 /100m) (2018) | 10:57 (01:28 /100m) (2019) |        **6.1%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    W     | 09:22 (01:15 /100m) (2021) | 09:59 (01:20 /100m) (2024) |        **6.3%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    W     | 18:35 (01:14 /100m) (2018) | 19:51 (01:19 /100m) (2019) |        **6.4%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    M     | 08:30 (01:08 /100m) (2020) | 09:05 (01:13 /100m) (2024) |        **6.4%**        |
|                      [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                       | OLYMPIC  |    W     | 18:22 (01:13 /100m) (2024) | 19:38 (01:19 /100m) (2021) |        **6.5%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 18:02 (01:12 /100m) (2015) | 19:18 (01:17 /100m) (2016) |        **6.5%**        |
|  [Yokohama](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: )   | OLYMPIC  |    M     | 17:33 (01:10 /100m) (2014) | 18:47 (01:15 /100m) (2011) |        **6.6%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:58 (01:16 /100m) (2014) | 20:23 (01:22 /100m) (2016) |        **6.9%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                  | OLYMPIC  |    W     | 17:26 (01:10 /100m) (2014) | 18:46 (01:15 /100m) (2015) |        **7.2%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    M     | 08:30 (01:08 /100m) (2020) | 09:10 (01:13 /100m) (2015) |        **7.3%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    W     | 18:51 (01:15 /100m) (2018) | 20:23 (01:22 /100m) (2016) |        **7.5%**        |
| [Sydney](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_sydney) ( :australia: ) | OLYMPIC  |    W     | 19:38 (01:19 /100m) (2012) | 21:15 (01:25 /100m) (2010) |        **7.6%**        |
|                     [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                      |  SPRINT  |    W     | 09:07 (01:13 /100m) (2020) | 09:53 (01:19 /100m) (2015) |        **7.7%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    W     | 10:17 (01:22 /100m) (2018) | 11:09 (01:29 /100m) (2017) |        **7.7%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    M     | 16:59 (01:08 /100m) (2018) | 18:27 (01:14 /100m) (2019) |        **8.0%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    M     | 16:56 (01:08 /100m) (2021) | 18:27 (01:14 /100m) (2019) |        **8.2%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup) ( :kr: )                  |  SPRINT  |    M     | 08:11 (01:05 /100m) (2017) | 08:55 (01:11 /100m) (2016) |        **8.3%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    W     | 10:03 (01:20 /100m) (2023) | 10:57 (01:28 /100m) (2019) |        **8.3%**        |
|                   [San Diego](https://www.triathlon.org/events/event/2012_itu_world_triathlon_san_diego) ( :us: )                    | OLYMPIC  |    M     | 16:12 (01:05 /100m) (2013) | 17:41 (01:11 /100m) (2012) |        **8.3%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    W     | 18:08 (01:13 /100m) (2023) | 19:51 (01:19 /100m) (2019) |        **8.7%**        |
|             [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )              |  SPRINT  |    W     | 09:07 (01:13 /100m) (2020) | 09:59 (01:20 /100m) (2024) |        **8.7%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    M     | 08:51 (01:11 /100m) (2014) | 09:42 (01:18 /100m) (2019) |        **8.8%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    W     | 18:06 (01:12 /100m) (2022) | 19:51 (01:19 /100m) (2019) |        **8.8%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 17:33 (01:10 /100m) (2014) | 19:18 (01:17 /100m) (2016) |        **9.1%**        |
|                    [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                     | OLYMPIC  |    M     | 17:31 (01:10 /100m) (2018) | 19:18 (01:17 /100m) (2016) |        **9.2%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    W     | 09:56 (01:19 /100m) (2015) | 10:57 (01:28 /100m) (2019) |        **9.3%**        |
|                 [Stockholm](https://www.triathlon.org/events/event/2015_itu_world_triathlon_stockholm) ( :sweden: )                  | OLYMPIC  |    M     | 17:42 (01:11 /100m) (2016) | 19:32 (01:18 /100m) (2015) |        **9.4%**        |
|                  [Montreal](https://www.triathlon.org/events/event/2019_itu_world_triathlon_montreal) ( :canada: )                   |  SPRINT  |    M     | 08:09 (01:05 /100m) (2023) | 09:00 (01:12 /100m) (2019) |        **9.4%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    M     | 16:40 (01:07 /100m) (2022) | 18:27 (01:14 /100m) (2019) |        **9.7%**        |
|                 [Tongyeong](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup) ( :kr: )                  |  SPRINT  |    M     | 08:00 (01:04 /100m) (2019) | 08:55 (01:11 /100m) (2016) |       **10.4%**        |
|        [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | OLYMPIC  |    M     | 16:27 (01:06 /100m) (2023) | 18:27 (01:14 /100m) (2019) |       **10.9%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    W     | 09:56 (01:19 /100m) (2015) | 11:09 (01:29 /100m) (2017) |       **10.9%**        |
| [Sydney](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_sydney) ( :australia: ) | OLYMPIC  |    W     | 19:38 (01:19 /100m) (2012) | 22:07 (01:28 /100m) (2011) |       **11.2%**        |
|          [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          |  SPRINT  |    M     | 08:33 (01:08 /100m) (2015) | 09:42 (01:18 /100m) (2019) |       **11.9%**        |
|                     [Chicago](https://www.triathlon.org/events/event/2014_itu_world_triathlon_chicago) ( :us: )                      | OLYMPIC  |    W     | 17:56 (01:12 /100m) (2015) | 20:26 (01:22 /100m) (2014) |       **12.3%**        |
|                     [Chicago](https://www.triathlon.org/events/event/2014_itu_world_triathlon_chicago) ( :us: )                      | OLYMPIC  |    M     | 16:31 (01:06 /100m) (2015) | 19:09 (01:17 /100m) (2014) |       **13.8%**        |

</details>

---

The benefit of the wetsuit could be estimated with a **third method** (more naive):

<details>
  <summary>Click to expand - <strong>Third approach.</strong></summary>

|             ![wetsuit_2.png](res/wetsuit_2.png)              | 
|:------------------------------------------------------------:| 
|   *Comparing duration of swims with and without wetsuit.*    |

The idea is to compare the **average swim durations**, **with-** and **without wetsuit**:
- `improve_percent = (time_no_wetsuit - time_wetsuit) / time_no_wetsuit`.
- This formula is applied to **four cases**: W-sprint, W-olympic, M-sprint, M-olympic. And results are written in the title of the above figure.
- Note how the **swim histograms** of the [:stopwatch: PACES](#stopwatch-paces) section **reveals two distinct modes**: **with-** (in violet, with lower times) and **without wetsuit** (larger times).

Outliers:
- The swim from [2012 Mooloolaba ITU Triathlon World Cup ( :australia: )](https://www.triathlon.org/events/event/2012_mooloolaba_itu_triathlon_world_cup) has been dropped, see the previous section on [T1](#T1).
- The **slowest swim** in the **olympic format**, for both men and women, occurred during **Paris 2024 Olympic Games** ( :fr: ).

:warning: **CRITICISMS**.
- This method incorporates **more data**, but yields **less reliable** results to the following factors:
  - :straight_ruler: **Swim course distances** vary between races.
  - :stopwatch: **Timing methods** (e.g., timing mat locations) are **not always consistent**.
- For exemple:
  - The **difference** between the fastest and the slowest `sprint`+`men`+`same-equipment` swim exceeds **2 minutes**.
    - Specifically, swim times at **Mooloolaba** ( :australia: ) are **unusually fast** considering the **absence of wetsuit**.
  - For `olympic`+`men`+`no-wetsuit`, the difference is **5:45**.
- Clearly, **swim distances** or **timing methods** vary between races, even when they are **labeled with the same format**.
- Nonetheless, we can hope that these variations will **balance out** thanks to the **large amount of data**.

</details>

---

### :bar_chart: Conclusion

**How much faster are top swimmers (5-9th) with the wetsuit?**
- Method 1: **`improve_percent = 5.4%`** (women only), leveraging events where the "`women-without` / `men-with-wetsuit` scenario" occurs.
  - **Refinements** of this method suggest **lower benefits**, around **4-5%**.
- Method 2: **`improve_percent = 3.6%`**, using on **year-to-year comparisons**.
- Method 3: **`improve_percent = 4.1%`** (olympic format only), naively comparing the overall average times _with_ and _without_ wetsuit.
- _Which method do you think is the most appropriate? What could be improved? If you have any comments or ideas, please do not hesitate to contact me!_

**Does the wetsuit benefit equally women and men?**
- The methods 2 and 3 suggest that **women benefit _slightly_ more from the wetsuit**, with a tiny improvement difference of 0.1-0.3%.
  - It that **statistically significant**?
  - This finding is somewhat surprising, given that women already have **a higher natural buoyancy**, which could suggest a smaller relative benefit.
  - The first method **could only compute `improve_percent` for women**, limiting direct comparability.

---

### :mortar_board: Literature review

Here are **some findings of related scientific works**:

- [This 2019 research by Gay et al.](https://pubmed.ncbi.nlm.nih.gov/30958047/) asked 33 swimmers to perform 2×400-m maximal front crawl in a 25-m swimming pool, with wetsuit and with swimsuit. Participants were good swimmers, but not as fast as ITU elite athletes: **1:27 / 100m** average on the 400m with swimsuit.
  - The **wetsuit** allows for a **~6% improvement**.
  - Interestingly: _"Swimmers **reduced stroke rate** and **increased stroke length** (by 4%) to benefit from the hydrodynamic reduction of the wetsuit and increase their swimming efficiency."_
- [This 2022 meta study by Gay et al.](https://www.mdpi.com/2673-9488/2/4/16) concludes from 26 studies, a _"**3.2–12.9% velocity increments** in distances ranging from 25 to 1500 m"_ for the **full-body wetsuit**.
  - The range is broad: it depends on many factors such as the **profile of the swimmer** (age, level, triathlete or swimmer), the **swimming conditions** (temperature, 25m pool vs open water) and the **wetsuit** itself.
  - [This interview of Ana Gay in triathlete.com](https://www.triathlete.com/gear/swim/how-much-faster-does-a-wetsuit-make-you-swim/) gives a good introduction to her study.
  - Her PhD thesis can be found [here](https://digibug.ugr.es/bitstream/handle/10481/71400/73824.pdf).
- In [this episode by scientifictriathlon.com](https://scientifictriathlon.com/tts392/), [Maria Francesca Piacentini](https://www.researchgate.net/profile/Maria-Francesca-Piacentini) mentions some of her research on wetsuit, and **claims 6% to 11% improvements**.
  - Apart from the time reduction, her team found that **wetsuit usage** can make athletes **feel less fatigued**: during the [2x7x200m tests](https://www.researchgate.net/publication/366991271_The_Effects_of_a_Wetsuit_on_Biomechanical_Physiological_and_Perceptual_Variables_in_Experienced_Triathletes), the [**stroke index**](https://blog.tritonwear.com/interpreting-to-improving-stroke-index#:~:text=It's%20called%20the%20Stroke%20Index,dig%20further%20into%20this%20shortly.) and the **stroke length** significantly **decreased in the swimsuit** condition, whereas they remained relatively **stable in the wetsuit condition**.
- [This article from sports-performance-bulletin](https://www.sportsperformancebulletin.com/training/triathlon-clothing-the-benefits-of-wearing-a-wetsuit) reports **improvements by 3% to 7%**.
  - Sources are not explicitly referenced, but the article probably mentions [this 1995 research by Chatard et al.](https://www.researchgate.net/publication/15406796_Wet_suit_effect_A_comparison_between_competitive_swimmers_and_triathletes) which apart from computing improvements, shows that the **impact of the wetsuit** is very different for **competitive swimmers than for competitive triathletes**.

The **4-5% improvement** observed in top swimmers (ranked 5th-9th) based on **World Triathlon race data** appears to align reasonably well with the findings of related research publications.
- :warning: It is important to note that the **lab- or pool-conditions** used by **most studies differ significantly** from the **open-water race environment**.

---

### Is the wetsuit worth for 300m?

When they can choose, **pro athletes decide to use the wetsuit** for **~300m swim**, e.g. during **mixed team relay**. Examples:
  - [2018 Nottingham ( :gb: ) ](https://www.triathlon.org/results/result/2018_itu_world_triathlon_mixed_relay_series_nottingham/323321): [video](https://www.youtube.com/watch?v=B4LHN6GeTF4).
  - [2022 Leeds ( :gb: )](https://triathlon.org/results/result/2022_world_triathlon_championship_series_leeds/550671): [pic1](https://triathlon-uploads.imgix.net/webgalleries/163472/tomz2553.jpg) and [pic2](https://triathlon-uploads.imgix.net/webgalleries/163472/tomz2448.jpg).
  - [2023 Sunderland ( :gb: ) ](https://triathlon.org/results/result/2023_world_triathlon_championship_series_sunderland/576189): [video](https://www.youtube.com/watch?v=xufIoKMYlLo). (Here the wetsuit was mandatory: 13.7°C water :cold_face:)

**_Is this decision sound?_**

<details>
  <summary>Click to expand - 🐧 <strong>Answering the question <i>"wetsuit for 300m?"</i></strong></summary>

**Two quantities** must be compared:
- (1) How much **time is spent** for the wetsuit during T1?
  - According to [the next section](#shower-wetsuit-at-t1), the **extra-time added by the wetsuit during T1** is **around 9 seconds**.
  - _Before this analysis, I would have estimated a lower impact, around 6s._
- (2) How much **time is saved** by the wetsuit during the 300m swim?
  - According to the present section, the benefit of the wetsuit ranges **between 3.6% and 5.4%**.
  - _These estimates are based on the 1500m swim in Olympic-distance triathlons. Are they applicable to a 300m swim?_
  - A 300m swim typically takes between 3:30 and 4:00. See justification below.
  - Therefore, the **time saved** with a wetsuit is estimated to be **7.6 seconds** (`3.6% of 3:30`) and **13 seconds** (`5.4% of 4:00`).

:bulb: **Conclusion**
- `7.6 - 9 = -1.4  < 0`
- ` 13 - 9 =    4  > 0`
- Depending on the selected parameters, the **total wetsuit gain** for a 300m swim ranges **from -1.4 to 4.0 seconds**.
- Beyond **time saving**, wetsuits provide additional benefits:
  - **Temperature comfort** and potential **energy savings in the legs**.
  - Athletes may also gain a couple of seconds to **catch their breath** while removing it at T1?
- **Unique conditions**.
  - The 300m swim is featured in events like the [mixed team relay](https://www.youtube.com/watch?v=d2Z0cyUmvr8) and [supertri](https://supertri.com/), with **smaller fields** compared to the **55-athlete mass starts** typical of sprint or olympic formats.
  - Could it be more advantageous to **try to draft without a wetsuit** at the back of the small group, prioritizing a fast T1, rather than **fighting for a front position** and **risking delays from wetsuit removal failures**?
    - This is particularly relevant for the **first relay** athlete, as subsequent (2nd, 3rd, and 4th) often **swim in smaller groups or even alone**, reducing the drafting and position-fighting dynamics. 
  - Further research is needed to determine if **skipping the wetsuit in these particular contexts** could provide a **strategic advantage**.
- An **interesting real-world experiment**: At the [2024 Toulouse ( :fr: ) supertri](https://supertri.com/results/2024-toulouse-results-men/) some athletes **opted out of wetsuits** for the first 300m swim:
  - [5/16 women](https://www.youtube.com/watch?v=asUQlc3Ic98&t=666)
  - [5/16 men](https://www.youtube.com/watch?v=asUQlc3Ic98&t=5163)

---

Appendix: Deriving that 300m swim takes **about 3:30 - 4:00**.
- Here are some swim-times measured for 300m, **without wetsuit**:
  - The 5-th **man** out of water was at **~3:35** at [2024 Hamburg ( :de: )](https://youtu.be/WyfYD2wsHPg?t=76) during the first leg.
  - The 5-th **man** was at **~3:37** at [2023 Hamburg ( :de: )](https://youtu.be/nJ4sm5ULXj8?t=1322) during the first leg.
  - The 5-th **man** was at **~3:41** at [2023 Super-Sprint Hamburg ( :de: )](https://triathlon.org/results/result/2023_world_triathlon_sprint_relay_championships_hamburg/582516) .
  - The 5-th **women** was at **~3:46** at [2021 Tokyo ( :jp: )](https://youtu.be/oQQEa_je2Vg?t=777).
  - The 5-th **women** was at **~3:58** at [2018 Hamburg ( :de: )](https://youtu.be/oAwzJnX44Yg?t=42).
  - The 5-th **woman** was at **~4:05** at [2023 Super-Sprint Hamburg ( :de: )](https://triathlon.org/results/result/2023_world_triathlon_sprint_relay_championships_hamburg/582517).
- Variations occur depending on the **actual swim distance** (buoys positions) and the **position of the timing mat**.
- Considering the broad **range (3:30 - 4:00)** seems relevant for our computation.

| Benefit | 03:20 | 03:25 | 03:30 | 03:35 |  03:40   |  03:45   |  03:50   | 03:55 | 04:00 | 04:05 | 04:10 |
|:-------:|:-----:|:-----:|:-----:|:-----:|:--------:|:--------:|:--------:|:-----:|:-----:|:-----:|:-----:|
|  3.0%   |  6.0  |  6.1  |  6.3  |  6.4  |   6.6    |   6.8    |   6.9    |  7.0  |  7.2  |  7.4  |  7.5  |
|  3.2%   |  6.4  |  6.6  |  6.7  |  6.9  |   7.0    |   7.2    |   7.4    |  7.5  |  7.7  |  7.8  |  8.0  |
|  3.4%   |  6.8  |  7.0  |  7.1  |  7.3  |   7.5    |   7.6    |   7.8    |  8.0  |  8.2  |  8.3  |  8.5  |
|  3.6%   |  7.2  |  7.4  |  7.6  |  7.7  | **7.9**  | **8.1**  | **8.3**  |  8.5  |  8.6  |  8.8  |  9.0  |
|  3.8%   |  7.6  |  7.8  |  8.0  |  8.2  | **8.4**  | **8.6**  | **8.7**  |  8.9  |  9.1  |  9.3  |  9.5  |
|  4.0%   |  8.0  |  8.2  |  8.4  |  8.6  | **8.8**  | **9.0**  | **9.2**  |  9.4  |  9.6  |  9.8  | 10.0  |
|  4.2%   |  8.4  |  8.6  |  8.8  |  9.0  | **9.2**  | **9.5**  | **9.7**  |  9.9  | 10.1  | 10.3  | 10.5  |
|  4.4%   |  8.8  |  9.0  |  9.2  |  9.5  | **9.7**  | **9.9**  | **10.1** | 10.3  | 10.6  | 10.8  | 11.0  |
|  4.6%   |  9.2  |  9.4  |  9.7  |  9.9  | **10.1** | **10.4** | **10.6** | 10.8  | 11.0  | 11.3  | 11.5  |
|  4.8%   |  9.6  |  9.8  | 10.1  | 10.3  | **10.6** | **10.8** | **11.0** | 11.3  | 11.5  | 11.8  | 12.0  |
|  5.0%   | 10.0  | 10.3  | 10.5  | 10.8  | **11.0** | **11.3** | **11.5** | 11.8  | 12.0  | 12.3  | 12.5  |
|  5.2%   | 10.4  | 10.7  | 10.9  | 11.2  | **11.4** | **11.7** | **12.0** | 12.2  | 12.5  | 12.7  | 13.0  |
|  5.4%   | 10.8  | 11.1  | 11.3  | 11.6  | **11.9** | **12.2** | **12.4** | 12.7  | 13.0  | 13.2  | 13.5  |
|  5.6%   | 11.2  | 11.5  | 11.8  | 12.0  |   12.3   |   12.6   |   12.9   | 13.2  | 13.4  | 13.7  | 14.0  |
|  5.8%   | 11.6  | 11.9  | 12.2  | 12.5  |   12.8   |   13.1   |   13.3   | 13.6  | 13.9  | 14.2  | 14.5  |
|  6.0%   | 12.0  | 12.3  | 12.6  | 12.9  |   13.2   |   13.5   |   13.8   | 14.1  | 14.4  | 14.7  | 15.0  |
|  6.2%   | 12.4  | 12.7  | 13.0  | 13.3  |   13.6   |   14.0   |   14.3   | 14.6  | 14.9  | 15.2  | 15.5  |
|  6.4%   | 12.8  | 13.1  | 13.4  | 13.8  |   14.1   |   14.4   |   14.7   | 15.0  | 15.4  | 15.7  | 16.0  |
|  6.6%   | 13.2  | 13.5  | 13.9  | 14.2  |   14.5   |   14.9   |   15.2   | 15.5  | 15.8  | 16.2  | 16.5  |
|  6.8%   | 13.6  | 13.9  | 14.3  | 14.6  |   15.0   |   15.3   |   15.6   | 16.0  | 16.3  | 16.7  | 17.0  |

</details>

---

---

# :shower: WETSUIT AT T1

This section addresses the question:
> **"How much time does the wetsuit add to T1?"**

To answer this, the goal is to calculate:
```
extra_time_for_wetsuit = t1_with_wetsuit - t1_without_wetsuit
```

The challenge is that **only one of these two `t1_` values is typically available**: the one recorded during the race.
- In practice, when the wetsuit is allowed, **everyone wears it**.
  - It does not happen for a race to have groups of athletes split between wearing and not wearing wetsuits, which would have allowed direct measurement of both `t1_` times under the same conditions.
- Consequently, this section introduces **two methods** to **estimate the missing `t1_`**, enabling the calculation of the `extra_time_for_wetsuit` difference.

Note: For each race analysed, the average T1 duration is calculated, **excluding the 5 slowest transition times** to reduce the influence of outliers.

---

### :earth_africa: Method 1: Using **Recurring Events**

This method identifies **pairs of events** held at the **same venue**, where wetsuits were **required in one year** but **not in another**.
- The approach assumes that the **course layout remains consistent** across years and that **timing method** for T1 do not change significantly.
- For example, in the women’s race at Cagliari ( :italy: ), wetsuits were worn in 2024 (T1 time: `46.9s`) but not in 2023 (T1 time: `39.1s`) and not in 2022 (T1 time: `37.8s`).
- Using these **three events**, **two comparisons** can be made to estimate `extra_time_for_wetsuit`:
  - **2024 (wetsuit) vs 2023 (no-wetsuit):** `extra_time_for_wetsuit = 46.9s - 39.1s = 7.9s`.
  - **2024 (wetsuit) vs 2022 (no-wetsuit):** `extra_time_for_wetsuit = 46.9s - 37.8s = 9.1s`.
- By collecting many such comparisons, a **distribution of `extra_time_for_wetsuit`** is generated, see the following figure.
- The **mean and median** of this distribution provide an answer to the initial question: **_"How much time does the wetsuit add to T1?"_**

Limitations:
- The **exact length of T1** may vary if the course layout changes between years or if **timing mats** are moved.
  - Such differences can render comparisons inaccurate.
  - For instance, an **extra 15 meters** in T1 would add about **3 seconds** at a speed of 18 km/h. 
  - One option considered was to exclude comparisons between events that were **several years apart**. However, since the final results were not significantly affected, this rule was not applied to maintain a larger dataset.
- To address this, data cleaning is applied to remove implausible entries.
  - Determining the **appropriate upper threshold** for such exclusions remains a challenge: _15s? 20s? 30s?_
  - But this choice is not critical, as explained below.

Advantages:
- `extra_time_for_wetsuit` can be calculated separately for **men**, **women**, or **combined** datasets.
- The method benefits from a **large number of comparisons** (more than 300), improving the robustness of the estimate:
  - Variations in course length are **mitigated** since some comparisons will involve longer and others shorter T1 courses, **balancing the overall distribution**.
  - Outliers have minimal impact on the final aggregated estimate due to the **high volume of data points**. Testing with different thresholds did not show any significant difference in the final estimate.

|                                                        ![t1_with_wetsuit.png](res/t1_with_wetsuit.png)                                                         | 
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:| 
| *Distribution of the estimated `extra_time_for_wetsuit`, i.e. the **additional time charged to the wetsuit at T1**, using the method of **recurring events**.* |

Results from **270 comparisons**:
- The wetsuit **adds `9.3` (mean) or `9.2` (median) seconds in T1**. (`std = 2.7`)
- **Women are `0.1` (with means) or `0.4` (with medians) seconds slower** than men.
	- Women only: `mean = 9.4`, `median = 9.4`. (`std = 2.6`)
	- Men only: `mean = 9.3`, `median = 9.0`. (`std = 2.7`) 

- Restricting to **world-series** yields **`~9.6` extra seconds** (from 206 comparisons) **both for men and women**.

<details>
  <summary>Click to expand - ⚖️ <strong>Full list of comparisons used for this derivation.</strong></summary>

**Distributions:**
- Event category:
	- WTCS      : 80% (215)
	- World-Cup : 20% (55)
- Distance category:
	- Olympic   : 52% (140)
	- Sprint    : 48% (130)

**Venues of the comparisons:**
- 95 (35.2%): Hamburg ( :de: )
- 63 (23.3%): Yokohama ( :jp: )
- 28 (10.4%): Edmonton ( :canada: )
- 21 ( 7.8%): London ( :gb: )
- 20 ( 7.4%): Tongyeong ( :kr: )
- 13 ( 4.8%): New Plymouth ( :new_zealand: )
- 10 ( 3.7%): Karlovy Vary ( :czech_republic: )
-  7 ( 2.6%): Auckland ( :new_zealand: )
-  4 ( 1.5%): Cannigione, Arzachena ( :it: )
-  4 ( 1.5%): Cagliari ( :it: )
-  2 ( 0.7%): San Diego ( :us: )
-  2 ( 0.7%): Valencia ( :es: )
-  1 ( 0.4%): Stockholm ( :sweden: )

|                                                               EVENT                                                               |  GENDER  |  T1 WITH WETSUIT (s)  |  T1 WITHOUT WETSUIT (s)  |  **EXTRA TIME FOR WETSUIT (s)**  |
|:---------------------------------------------------------------------------------------------------------------------------------:|:--------:|:---------------------:|:------------------------:|:--------------------------------:|
|   [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      41.3 (2012)      |       37.3 (2009)        |             **4.0**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    W     |      66.7 (2023)      |       62.4 (2009)        |             **4.3**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    M     |      27.2 (2022)      |       22.8 (2019)        |             **4.3**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    M     |      48.5 (2017)      |       44.1 (2015)        |             **4.5**              |
|                  [Tongyeong](https://www.triathlon.org/events/event/2022_world_triathlon_cup_tongyeong) ( :kr: )                  |    M     |      37.0 (2021)      |       32.5 (2022)        |             **4.5**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    W     |      67.1 (2022)      |       62.4 (2009)        |             **4.8**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    M     |      27.7 (2023)      |       22.8 (2019)        |             **4.9**              |
|   [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      45.4 (2013)      |       40.3 (2011)        |             **5.0**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    W     |      39.9 (2019)      |       34.8 (2010)        |             **5.0**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    M     |      48.5 (2017)      |       43.3 (2016)        |             **5.2**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    M     |      38.8 (2016)      |       33.6 (2010)        |             **5.2**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      38.8 (2016)      |       33.6 (2022)        |             **5.3**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    W     |      52.2 (2017)      |       46.9 (2015)        |             **5.3**              |
|   [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      42.2 (2014)      |       36.8 (2011)        |             **5.4**              |
|   [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      45.7 (2014)      |       40.3 (2011)        |             **5.4**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    M     |      39.1 (2017)      |       33.6 (2010)        |             **5.5**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      39.1 (2017)      |       33.6 (2022)        |             **5.5**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      36.2 (2019)      |       30.6 (2024)        |             **5.6**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    M     |      39.2 (2009)      |       33.6 (2010)        |             **5.6**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      39.2 (2009)      |       33.6 (2022)        |             **5.6**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    M     |      61.6 (2023)      |       55.9 (2009)        |             **5.6**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    W     |      30.2 (2022)      |       24.6 (2019)        |             **5.7**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    W     |      30.3 (2023)      |       24.6 (2019)        |             **5.7**              |
|               [Edmonton](https://www.triathlon.org/events/event/2013_edmonton_itu_triathlon_world_cup) ( :canada: )               |    W     |      68.0 (2014)      |       62.2 (2013)        |             **5.8**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      42.2 (2009)      |       36.4 (2022)        |             **5.9**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    M     |      39.5 (2021)      |       33.6 (2010)        |             **5.9**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      39.5 (2021)      |       33.6 (2022)        |             **5.9**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      42.3 (2017)      |       36.4 (2022)        |             **5.9**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2014_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    M     |      48.5 (2017)      |       42.6 (2014)        |             **6.0**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      42.4 (2021)      |       36.4 (2022)        |             **6.0**              |
|   [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      39.8 (2012)      |       33.8 (2009)        |             **6.1**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      36.2 (2019)      |       30.1 (2015)        |             **6.1**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    M     |      61.6 (2023)      |       55.5 (2021)        |             **6.1**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      42.6 (2016)      |       36.4 (2022)        |             **6.2**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    W     |      30.5 (2018)      |       24.2 (2017)        |             **6.3**              |
|                  [Tongyeong](https://www.triathlon.org/events/event/2022_world_triathlon_cup_tongyeong) ( :kr: )                  |    M     |      38.9 (2019)      |       32.5 (2022)        |             **6.3**              |
|            [Cannigione, Arzachena](https://www.triathlon.org/events/event/2022_world_triathlon_cup_arzachena) ( :it: )            |    W     |      48.2 (2020)      |       41.9 (2022)        |             **6.4**              |
|                  [Tongyeong](https://www.triathlon.org/events/event/2022_world_triathlon_cup_tongyeong) ( :kr: )                  |    W     |      41.5 (2021)      |       35.1 (2022)        |             **6.4**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      39.9 (2019)      |       33.4 (2015)        |             **6.5**              |
|               [Edmonton](https://www.triathlon.org/events/event/2013_edmonton_itu_triathlon_world_cup) ( :canada: )               |    W     |      68.8 (2021)      |       62.2 (2013)        |             **6.5**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    M     |      28.2 (2017)      |       21.6 (2019)        |             **6.5**              |
|                  [Tongyeong](https://www.triathlon.org/events/event/2022_world_triathlon_cup_tongyeong) ( :kr: )                  |    W     |      41.7 (2019)      |       35.1 (2022)        |             **6.5**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    W     |      31.1 (2021)      |       24.6 (2019)        |             **6.6**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    W     |      30.8 (2014)      |       24.2 (2017)        |             **6.6**              |
|                [Stockholm](https://www.triathlon.org/events/event/2015_itu_world_triathlon_stockholm) ( :sweden: )                |    M     |      51.7 (2016)      |       45.1 (2015)        |             **6.6**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    W     |      66.7 (2023)      |       60.1 (2021)        |             **6.6**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      36.2 (2019)      |       29.5 (2013)        |             **6.6**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2011_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    M     |      52.6 (2009)      |       45.9 (2011)        |             **6.6**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    W     |      69.1 (2015)      |       62.4 (2009)        |             **6.7**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      36.2 (2019)      |       29.4 (2018)        |             **6.7**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    M     |      28.4 (2018)      |       21.6 (2019)        |             **6.7**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      61.6 (2023)      |       54.8 (2017)        |             **6.8**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    W     |      69.2 (2024)      |       62.4 (2009)        |             **6.8**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      43.3 (2012)      |       36.4 (2022)        |             **6.9**              |
|                  [Tongyeong](https://www.triathlon.org/events/event/2022_world_triathlon_cup_tongyeong) ( :kr: )                  |    M     |      39.4 (2023)      |       32.5 (2022)        |             **6.9**              |
|                 [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      68.0 (2014)      |       61.1 (2019)        |             **7.0**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      36.2 (2019)      |       29.2 (2014)        |             **7.0**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    W     |      67.1 (2022)      |       60.1 (2021)        |             **7.1**              |
|   [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      43.9 (2013)      |       36.8 (2011)        |             **7.1**              |
|          [Yokohama](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_yokohama1) ( :jp: )           |    M     |      61.6 (2023)      |       54.5 (2024)        |             **7.1**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    W     |      69.6 (2018)      |       62.4 (2009)        |             **7.2**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    M     |      30.0 (2020)      |       22.8 (2019)        |             **7.2**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    W     |      30.5 (2018)      |       23.3 (2019)        |             **7.2**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      39.9 (2019)      |       32.7 (2024)        |             **7.2**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      39.9 (2019)      |       32.6 (2013)        |             **7.2**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    M     |      30.1 (2021)      |       22.8 (2019)        |             **7.3**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    W     |      31.5 (2016)      |       24.2 (2017)        |             **7.3**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    W     |      69.7 (2014)      |       62.4 (2009)        |             **7.3**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    W     |      42.2 (2009)      |       34.8 (2010)        |             **7.4**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    M     |      63.4 (2015)      |       55.9 (2009)        |             **7.4**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    W     |      42.3 (2017)      |       34.8 (2010)        |             **7.5**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    M     |      63.4 (2018)      |       55.9 (2009)        |             **7.5**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    W     |      30.8 (2014)      |       23.3 (2019)        |             **7.5**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      61.6 (2023)      |       54.0 (2016)        |             **7.5**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    W     |      42.4 (2021)      |       34.8 (2010)        |             **7.6**              |
|           [Cagliari](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_cagliari) ( :it: )           |    W     |      46.3 (2024)      |       38.8 (2023)        |             **7.6**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    W     |      32.2 (2020)      |       24.6 (2019)        |             **7.6**              |
|   [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      44.4 (2015)      |       36.8 (2011)        |             **7.6**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      66.7 (2023)      |       59.0 (2017)        |             **7.7**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      66.7 (2023)      |       59.0 (2016)        |             **7.7**              |
|                 [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      68.8 (2021)      |       61.1 (2019)        |             **7.7**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    W     |      54.6 (2014)      |       46.9 (2015)        |             **7.7**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    M     |      29.5 (2014)      |       21.6 (2019)        |             **7.8**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    W     |      42.6 (2016)      |       34.8 (2010)        |             **7.8**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      39.9 (2019)      |       32.0 (2018)        |             **7.9**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    M     |      63.4 (2015)      |       55.5 (2021)        |             **7.9**              |
|                 [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      62.5 (2014)      |       54.6 (2019)        |             **8.0**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    M     |      63.4 (2018)      |       55.5 (2021)        |             **8.0**              |
|            [Cannigione, Arzachena](https://www.triathlon.org/events/event/2022_world_triathlon_cup_arzachena) ( :it: )            |    W     |      49.9 (2021)      |       41.9 (2022)        |             **8.0**              |
|   [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      45.4 (2013)      |       37.3 (2009)        |             **8.1**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      67.1 (2022)      |       59.0 (2017)        |             **8.1**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      67.1 (2022)      |       59.0 (2016)        |             **8.1**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      39.9 (2019)      |       31.7 (2014)        |             **8.1**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    M     |      31.0 (2018)      |       22.8 (2019)        |             **8.2**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      38.8 (2016)      |       30.6 (2024)        |             **8.2**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    W     |      31.5 (2016)      |       23.3 (2019)        |             **8.2**              |
|                  [Tongyeong](https://www.triathlon.org/events/event/2022_world_triathlon_cup_tongyeong) ( :kr: )                  |    W     |      43.4 (2023)      |       35.1 (2022)        |             **8.3**              |
|   [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      42.2 (2014)      |       33.8 (2009)        |             **8.4**              |
|   [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      45.7 (2014)      |       37.3 (2009)        |             **8.4**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    W     |      43.3 (2012)      |       34.8 (2010)        |             **8.5**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      39.1 (2017)      |       30.6 (2024)        |             **8.5**              |
|          [Cannigione, Arzachena](https://www.triathlon.org/events/event/2020_arzachena_itu_triathlon_world_cup) ( :it: )          |    M     |      46.4 (2021)      |       37.9 (2020)        |             **8.5**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    M     |      42.1 (2012)      |       33.6 (2010)        |             **8.5**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    M     |      52.6 (2009)      |       44.1 (2015)        |             **8.5**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      42.1 (2012)      |       33.6 (2022)        |             **8.5**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      39.2 (2009)      |       30.6 (2024)        |             **8.6**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      66.7 (2023)      |       58.1 (2019)        |             **8.6**              |
|                  [Tongyeong](https://www.triathlon.org/events/event/2022_world_triathlon_cup_tongyeong) ( :kr: )                  |    M     |      41.1 (2018)      |       32.5 (2022)        |             **8.6**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      63.4 (2015)      |       54.8 (2017)        |             **8.6**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      63.4 (2018)      |       54.8 (2017)        |             **8.7**              |
|               [Edmonton](https://www.triathlon.org/events/event/2013_edmonton_itu_triathlon_world_cup) ( :canada: )               |    W     |      70.9 (2016)      |       62.2 (2013)        |             **8.7**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    M     |      30.4 (2016)      |       21.6 (2019)        |             **8.7**              |
|            [Cannigione, Arzachena](https://www.triathlon.org/events/event/2022_world_triathlon_cup_arzachena) ( :it: )            |    M     |      46.4 (2021)      |       37.7 (2022)        |             **8.7**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      38.8 (2016)      |       30.1 (2015)        |             **8.7**              |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    M     |      42.4 (2011)      |       33.6 (2010)        |             **8.8**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      42.4 (2011)      |       33.6 (2022)        |             **8.8**              |
|           [Cagliari](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_cagliari) ( :it: )           |    W     |      46.3 (2024)      |       37.5 (2022)        |             **8.8**              |
|       [Karlovy Vary](https://www.triathlon.org/events/event/2019_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )       |    W     |      33.4 (2018)      |       24.6 (2019)        |             **8.8**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      39.5 (2021)      |       30.6 (2024)        |             **8.9**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.2 (2009)      |       33.4 (2015)        |             **8.9**              |
|   [London](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      49.2 (2015)      |       40.3 (2011)        |             **8.9**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    M     |      30.5 (2015)      |       21.6 (2019)        |             **8.9**              |
|           [Yokohama](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama) ( :jp: )           |    M     |      61.6 (2023)      |       52.7 (2022)        |             **8.9**              |
|          [Yokohama](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_yokohama1) ( :jp: )           |    M     |      63.4 (2015)      |       54.5 (2024)        |             **8.9**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.3 (2017)      |       33.4 (2015)        |             **8.9**              |
|   [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      41.3 (2012)      |       32.4 (2010)        |             **9.0**              |
|          [Yokohama](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_yokohama1) ( :jp: )           |    M     |      63.4 (2018)      |       54.5 (2024)        |             **9.0**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.4 (2021)      |       33.4 (2015)        |             **9.0**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.1 (2017)      |       30.1 (2015)        |             **9.0**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      61.6 (2023)      |       52.6 (2019)        |             **9.0**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      67.1 (2022)      |       58.1 (2019)        |             **9.0**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    W     |      69.1 (2015)      |       60.1 (2021)        |             **9.0**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.2 (2009)      |       30.1 (2015)        |             **9.1**              |
|   [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      39.8 (2012)      |       30.7 (2010)        |             **9.1**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    W     |      69.2 (2024)      |       60.1 (2021)        |             **9.1**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    M     |      52.6 (2009)      |       43.3 (2016)        |             **9.2**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.6 (2016)      |       33.4 (2015)        |             **9.2**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      38.8 (2016)      |       29.5 (2013)        |             **9.3**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    W     |      56.2 (2009)      |       46.9 (2015)        |             **9.3**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      63.4 (2015)      |       54.0 (2016)        |             **9.3**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.5 (2021)      |       30.1 (2015)        |             **9.4**              |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      63.4 (2018)      |       54.0 (2016)        |             **9.4**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      38.8 (2016)      |       29.4 (2018)        |             **9.4**              |
|                 [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      64.0 (2016)      |       54.6 (2019)        |             **9.4**              |
|        [New Plymouth](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    W     |      33.6 (2015)      |       24.2 (2017)        |             **9.5**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    W     |      69.6 (2018)      |       60.1 (2021)        |             **9.5**              |
| [Yokohama](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama) ( :jp: ) |    M     |      65.4 (2014)      |       55.9 (2009)        |             **9.5**              |
|                  [Tongyeong](https://www.triathlon.org/events/event/2022_world_triathlon_cup_tongyeong) ( :kr: )                  |    W     |      44.6 (2018)      |       35.1 (2022)        |             **9.5**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.1 (2017)      |       29.5 (2013)        |             **9.5**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      42.2 (2009)      |       32.7 (2024)        |             **9.6**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.2 (2009)      |       29.5 (2013)        |             **9.6**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    W     |      69.7 (2014)      |       60.1 (2021)        |             **9.6**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.2 (2009)      |       32.6 (2013)        |             **9.6**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.1 (2017)      |       29.4 (2018)        |             **9.6**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      42.3 (2017)      |       32.7 (2024)        |             **9.7**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.3 (2017)      |       32.6 (2013)        |             **9.7**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      38.8 (2016)      |       29.2 (2014)        |             **9.7**              |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      42.4 (2021)      |       32.7 (2024)        |             **9.7**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.2 (2009)      |       29.4 (2018)        |             **9.7**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.4 (2021)      |       32.6 (2013)        |             **9.7**              |
|                [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    W     |      56.8 (2011)      |       46.9 (2015)        |             **9.8**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      43.3 (2012)      |       33.4 (2015)        |             **9.9**              |
|                 [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      70.9 (2016)      |       61.1 (2019)        |             **9.9**              |
|            [Hamburg](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      46.3 (2011)      |       36.4 (2022)        |             **9.9**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.5 (2021)      |       29.5 (2013)        |             **9.9**              |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.1 (2017)      |       29.2 (2014)        |             **9.9**              |
|                     [Yokohama](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama) ( :jp: )                     |    M     |      65.4 (2014)      |       55.5 (2021)        |             **10.0**             |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      42.6 (2016)      |       32.7 (2024)        |             **10.0**             |
|                [Tongyeong](https://www.triathlon.org/events/event/2014_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    M     |      52.6 (2009)      |       42.6 (2014)        |             **10.0**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.2 (2009)      |       29.2 (2014)        |             **10.0**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.6 (2016)      |       32.6 (2013)        |             **10.0**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.5 (2021)      |       29.4 (2018)        |             **10.0**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.1 (2015)      |       59.0 (2017)        |             **10.1**             |
|             [Edmonton](https://www.triathlon.org/events/event/2021_world_triathlon_grand_final_edmonton) ( :canada: )             |    M     |      62.5 (2014)      |       52.5 (2021)        |             **10.1**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.1 (2015)      |       59.0 (2016)        |             **10.1**             |
|   [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      43.9 (2013)      |       33.8 (2009)        |             **10.1**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.2 (2024)      |       59.0 (2017)        |             **10.2**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.2 (2024)      |       59.0 (2016)        |             **10.2**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      68.0 (2014)      |       57.8 (2017)        |             **10.2**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.2 (2009)      |       32.0 (2018)        |             **10.3**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      39.5 (2021)      |       29.2 (2014)        |             **10.3**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.3 (2017)      |       32.0 (2018)        |             **10.3**             |
|        [New Plymouth](https://www.triathlon.org/events/event/2019_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )         |    W     |      33.6 (2015)      |       23.3 (2019)        |             **10.4**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      62.5 (2014)      |       52.1 (2017)        |             **10.4**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.4 (2021)      |       32.0 (2018)        |             **10.4**             |
|                [Tongyeong](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup) ( :kr: )                |    W     |      57.4 (2016)      |       46.9 (2015)        |             **10.4**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.2 (2009)      |       31.7 (2014)        |             **10.5**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.6 (2018)      |       59.0 (2017)        |             **10.5**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.6 (2018)      |       59.0 (2016)        |             **10.5**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.3 (2017)      |       31.7 (2014)        |             **10.6**             |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      43.3 (2012)      |       32.7 (2024)        |             **10.6**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      43.3 (2012)      |       32.6 (2013)        |             **10.6**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.4 (2021)      |       31.7 (2014)        |             **10.6**             |
|   [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      44.4 (2015)      |       33.8 (2009)        |             **10.7**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      65.4 (2014)      |       54.8 (2017)        |             **10.7**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.7 (2014)      |       59.0 (2017)        |             **10.7**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      65.3 (2015)      |       54.6 (2019)        |             **10.7**             |
|           [Yokohama](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama) ( :jp: )           |    M     |      63.4 (2015)      |       52.7 (2022)        |             **10.7**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.7 (2014)      |       59.0 (2016)        |             **10.7**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.6 (2016)      |       32.0 (2018)        |             **10.7**             |
|           [Yokohama](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama) ( :jp: )           |    M     |      63.4 (2018)      |       52.7 (2022)        |             **10.7**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      63.4 (2015)      |       52.6 (2019)        |             **10.8**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      63.4 (2018)      |       52.6 (2019)        |             **10.9**             |
|               [Edmonton](https://www.triathlon.org/events/event/2013_edmonton_itu_triathlon_world_cup) ( :canada: )               |    W     |      73.1 (2015)      |       62.2 (2013)        |             **10.9**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      68.8 (2021)      |       57.8 (2017)        |             **10.9**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      42.6 (2016)      |       31.7 (2014)        |             **10.9**             |
|          [Yokohama](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_yokohama1) ( :jp: )           |    M     |      65.4 (2014)      |       54.5 (2024)        |             **10.9**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.1 (2015)      |       58.1 (2019)        |             **10.9**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.2 (2024)      |       58.1 (2019)        |             **11.1**             |
|                  [San Diego](https://www.triathlon.org/events/event/2012_itu_world_triathlon_san_diego) ( :us: )                  |    M     |      69.1 (2013)      |       57.9 (2012)        |             **11.3**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      43.3 (2012)      |       32.0 (2018)        |             **11.3**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      65.4 (2014)      |       54.0 (2016)        |             **11.4**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.6 (2018)      |       58.1 (2019)        |             **11.4**             |
|   [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      42.2 (2014)      |       30.7 (2010)        |             **11.4**             |
|  [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )  |    W     |      46.3 (2011)      |       34.8 (2010)        |             **11.5**             |
|              [Auckland](https://www.triathlon.org/events/event/2015_itu_world_triathlon_auckland) ( :new_zealand: )               |    M     |      65.2 (2011)      |       53.7 (2015)        |             **11.5**             |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      42.1 (2012)      |       30.6 (2024)        |             **11.5**             |
|             [Edmonton](https://www.triathlon.org/events/event/2021_world_triathlon_grand_final_edmonton) ( :canada: )             |    M     |      64.0 (2016)      |       52.5 (2021)        |             **11.5**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      43.3 (2012)      |       31.7 (2014)        |             **11.5**             |
|                  [San Diego](https://www.triathlon.org/events/event/2012_itu_world_triathlon_san_diego) ( :us: )                  |    W     |      75.5 (2013)      |       64.0 (2012)        |             **11.5**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      69.7 (2014)      |       58.1 (2019)        |             **11.6**             |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    M     |      42.4 (2011)      |       30.6 (2024)        |             **11.8**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      64.0 (2016)      |       52.1 (2017)        |             **11.9**             |
|   [London](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      49.2 (2015)      |       37.3 (2009)        |             **11.9**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      42.1 (2012)      |       30.1 (2015)        |             **12.0**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      73.1 (2015)      |       61.1 (2019)        |             **12.1**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      68.0 (2014)      |       55.8 (2018)        |             **12.2**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      62.5 (2014)      |       50.3 (2018)        |             **12.3**             |
|              [Auckland](https://www.triathlon.org/events/event/2015_itu_world_triathlon_auckland) ( :new_zealand: )               |    W     |      71.3 (2011)      |       59.0 (2015)        |             **12.3**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      42.4 (2011)      |       30.1 (2015)        |             **12.3**             |
|              [Auckland](https://www.triathlon.org/events/event/2014_itu_world_triathlon_auckland) ( :new_zealand: )               |    M     |      65.2 (2011)      |       52.7 (2014)        |             **12.5**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      42.1 (2012)      |       29.5 (2013)        |             **12.5**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      42.1 (2012)      |       29.4 (2018)        |             **12.7**             |
|           [Yokohama](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama) ( :jp: )           |    M     |      65.4 (2014)      |       52.7 (2022)        |             **12.7**             |
|             [Edmonton](https://www.triathlon.org/events/event/2021_world_triathlon_grand_final_edmonton) ( :canada: )             |    M     |      65.3 (2015)      |       52.5 (2021)        |             **12.8**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      42.4 (2011)      |       29.5 (2013)        |             **12.8**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2019_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      65.4 (2014)      |       52.6 (2019)        |             **12.8**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2015_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      46.3 (2011)      |       33.4 (2015)        |             **12.9**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      42.1 (2012)      |       29.2 (2014)        |             **12.9**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      42.4 (2011)      |       29.4 (2018)        |             **12.9**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      68.8 (2021)      |       55.8 (2018)        |             **13.0**             |
|   [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      45.4 (2013)      |       32.4 (2010)        |             **13.0**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      70.9 (2016)      |       57.8 (2017)        |             **13.1**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      65.3 (2015)      |       52.1 (2017)        |             **13.1**             |
|   [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      43.9 (2013)      |       30.7 (2010)        |             **13.1**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    M     |      42.4 (2011)      |       29.2 (2014)        |             **13.2**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      61.6 (2023)      |       48.2 (2012)        |             **13.4**             |
|   [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    W     |      45.7 (2014)      |       32.4 (2010)        |             **13.4**             |
|                   [Valencia](https://www.triathlon.org/events/event/2022_world_triathlon_cup_valencia) ( :es: )                   |    W     |      53.0 (2020)      |       39.6 (2022)        |             **13.4**             |
|                   [Valencia](https://www.triathlon.org/events/event/2022_world_triathlon_cup_valencia) ( :es: )                   |    M     |      49.9 (2020)      |       36.3 (2022)        |             **13.5**             |
|            [Hamburg](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_hamburg) ( :de: )            |    W     |      46.3 (2011)      |       32.7 (2024)        |             **13.6**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      46.3 (2011)      |       32.6 (2013)        |             **13.7**             |
|   [London](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )   |    M     |      44.4 (2015)      |       30.7 (2010)        |             **13.7**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      64.0 (2016)      |       50.3 (2018)        |             **13.7**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2019_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      68.7 (2011)      |       54.6 (2019)        |             **14.1**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2018_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      46.3 (2011)      |       32.0 (2018)        |             **14.3**             |
|                 [Cagliari](https://www.triathlon.org/events/event/2018_cagliari_itu_triathlon_world_cup) ( :it: )                 |    W     |      59.7 (2016)      |       45.3 (2018)        |             **14.4**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      66.7 (2023)      |       52.3 (2012)        |             **14.4**             |
|                    [Hamburg](https://www.triathlon.org/events/event/2014_itu_world_triathlon_hamburg) ( :de: )                    |    W     |      46.3 (2011)      |       31.7 (2014)        |             **14.6**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                   |    W     |      67.1 (2022)      |       52.3 (2012)        |             **14.9**             |
|              [Auckland](https://www.triathlon.org/events/event/2015_itu_world_triathlon_auckland) ( :new_zealand: )               |    M     |      68.6 (2012)      |       53.7 (2015)        |             **14.9**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                 |    M     |      65.3 (2015)      |       50.3 (2018)        |             **15.0**             |
|              [Auckland](https://www.triathlon.org/events/event/2014_itu_world_triathlon_auckland) ( :new_zealand: )               |    W     |      71.3 (2011)      |       56.2 (2014)        |             **15.1**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2018_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      70.9 (2016)      |       55.8 (2018)        |             **15.2**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      63.4 (2015)      |       48.2 (2012)        |             **15.2**             |
|                   [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                   |    M     |      63.4 (2018)      |       48.2 (2012)        |             **15.2**             |
|                 [Edmonton](https://www.triathlon.org/events/event/2017_itu_world_triathlon_edmonton) ( :canada: )                 |    W     |      73.1 (2015)      |       57.8 (2017)        |             **15.3**             |
|              [Auckland](https://www.triathlon.org/events/event/2015_itu_world_triathlon_auckland) ( :new_zealand: )               |    W     |      74.9 (2012)      |       59.0 (2015)        |             **15.9**             |
|              [Auckland](https://www.triathlon.org/events/event/2014_itu_world_triathlon_auckland) ( :new_zealand: )               |    M     |      68.6 (2012)      |       52.7 (2014)        |             **16.0**             |
|                 [Cagliari](https://www.triathlon.org/events/event/2017_cagliari_itu_triathlon_world_cup) ( :it: )                 |    W     |      59.7 (2016)      |       43.7 (2017)        |             **16.0**             |


</details>

---

### :couple: Method 2: using **women/men differences**

The method leverages the **women/men comparison**, resembling the [approach to estimate the **benefit of the wetsuit**](#penguin-wetsuit-benefit).

As a riminder, the **formula** to compute the **extra-time for wetsuit** is:
```
extra_time_for_wetsuit = t1_with_wetsuit - t1_no_wetsuit
```

Let's consider as an example the [2024 Cagliari ( :italy: )](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_cagliari) event:
- This event is **very special** because **women raced with wetsuits**, while **men did not**.
- Trying to apply the formula for women:
  - `t1_with_wetsuit` is **known**.
  - `t1_no_wetsuit` is **unknown**.
- To estimate the **missing `t1_no_wetsuit` for women**, we introduce a **function**, `f_from_men_to_women_no_wetsuit`:
  - Input: `t1_no_wetsuit` for men.
  - Output: `t1_no_wetsuit` for women in the same event.
- Using this function, the **women's extra-time for wetsuit** can be computed:
  - `extra_time_for_wetsuit_women = t1_with_wetsuit_women - f(t1_no_wetsuit_men)`
- This approach will be repeated for all events where **women used wetsuits and men did not**: see the table below.

How to **derive the `f_from_men_to_women_no_wetsuit` function**?
- Using all events where **both men and women swam without wetsuits**.

**What model** for this `f_from_men_to_women_no_wetsuit` function?
- It is a **design choice**: _A linear model? An affine model? A more complex function approximation such as a neural network? How many layers and parameters then?_
- I have decided to model T1 as a **composition of two parts**:
  - **Static part:** The athlete **stands in front of the bike**, drop the swimming equipments (goggles and caps) into the box, and **put the helmet on**. Reminder: both women and men without wetsuit here.
  - **Moving part:** The athlete **runs** from the water to the bike, and then **runs pushing the bike** until the mounting line at the end of the blue carpet.
- I have made the following **assumptions**:
  - The duration of the static part, named **`helmet_duration`**, is **identical for men and women**.
  - Women are assumed to **run slower than men** by a **constant percentage**, **`diff_wm_t1_run`**.
    - `diff_wm_t1_run = (t1_run_women - t1_run_men) / t1_run_men`, where:
      - `t1_run_women = t1_women - helmet_duration`
      - `t1_run_men = t1_men - helmet_duration`

The resulting model to **estimate the missing `t1_no_wetsuit` for women** is:
```
t1_women_no_wetsuit = f(t1_men_no_wetsuit)
                    = (t1_men_no_wetsuit - helmet_duration) * (1 + diff_wm_t1_run) + helmet_duration`
```

Parameters:
- `helmet_duration` is set to **3s**.
  - Testing **values of 1 or 5 seconds** showed variations of less than 0.15 seconds in the final `extra_time_for_wetsuit` estimate.
- `diff_wm_t1_run` is estimating using the **147 events** where both women and men swam without wetsuit.
  - It is found to be **`10.0%`**, i.e. **women run 10% slower than men during T1**.
  - This value is further discussed in a subsequent paragraph.

The derived `f_from_men_to_women_no_wetsuit` function is applied to events featuring the **women-without / men-with** scenario:

| YEAR  |                                                      EVENT                                                      | **EXTRA TIME FOR WETSUIT** (s) (women)  | EVENT CATEGORY |
|:-----:|:---------------------------------------------------------------------------------------------------------------:|:---------------------------------------:|:--------------:|
| 2011  |       [Tongyeong](https://www.triathlon.org/events/event/2011_tongyeong_itu_triathlon_world_cup) ( :kr: )       |                 **6.5**                 |   WORLD-CUP    |
| 2020  | [Cannigione, Arzachena](https://www.triathlon.org/events/event/2020_arzachena_itu_triathlon_world_cup) ( :it: ) |                 **6.8**                 |   WORLD-CUP    |
| 2021  |          [Haeundae](https://www.triathlon.org/events/event/2021_world_triathlon_cup_haeundae) ( :kr: )          |                 **7.8**                 |   WORLD-CUP    |
| 2014  |       [Tongyeong](https://www.triathlon.org/events/event/2014_tongyeong_itu_triathlon_world_cup) ( :kr: )       |                 **8.1**                 |   WORLD-CUP    |
| 2024  |  [Cagliari](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_cagliari) ( :it: )  |                 **8.6**                 |      WTCS      |
| 2012  |        [Sydney](https://www.triathlon.org/events/event/2012_itu_world_triathlon_sydney) ( :australia: )         |                 **8.8**                 |      WTCS      |
| 2022  |  [Yokohama](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama) ( :jp: )  |                 **9.5**                 |      WTCS      |
| 2024  | [Yokohama](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_yokohama1) ( :jp: )  |                 **9.6**                 |      WTCS      |
| 2015  |       [Stockholm](https://www.triathlon.org/events/event/2015_itu_world_triathlon_stockholm) ( :sweden: )       |                 **9.9**                 |      WTCS      |
| 2016  |       [Tongyeong](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup) ( :kr: )       |                **10.0**                 |   WORLD-CUP    |
| 2021  |    [Edmonton](https://www.triathlon.org/events/event/2021_world_triathlon_grand_final_edmonton) ( :canada: )    |                **11.3**                 |      WTCS      |

Results:
- mean = median = **8.8 seconds** (from 11 events).
- Restricting to **world-series**:
  - The w/m difference for **running during T1** stays around 10% (**9.8%**) (from 59 events).
  - The estimated `extra_time_for_wetsuit` for women raises by ~1s to **9.7 seconds** (from 6 events).

Notes:
- Using the women/men comparison offers a strong advantage: the **exact distance** of T1 **does not matter**, as the course and timing methods are **identical for both genders**.
- One limitation: this method **relies on rare events** where women raced with wetsuits while men did not, or inversely for the men-estimate but the scenario is even rarer.

---

:bulb: **FINDINGS AND DISCUSSION:**
- **Both methods** to estimate `extra_time_for_wetsuit` yield **similar results**:
  - The **time charged to the wetsuit** during the T1 transition lays **around 9 seconds**.
    - For **world-series events**, it is a bit higher: **around 10 seconds**.
  - These estimations could serve as **training references for coaches and athletes**.
- I would first have **expected a lower time**.
  - However, T1 involves **more than just removing the wetsuit** in front of the bike.
  - Athletes must also run while wearing the wetsuit, which is **heavy and elastic**.
  - Additionally, they need to **unzip the wetsuit**, begin **removing the sleeves while running**, and ensure it is **properly placed in the designated box**.
- Two additional findings regarding the **women/men comparison**:
  - Women appear **slightly more affected** by the wetsuit.
    - But the **difference is tiny: < 0.4s**, and completely **negligible at the world-series level**.
  - **Women run 10% slower** than men during T1.
    - This percentage can be compared to the results of [the women/men comparison section](#couple-women-vs-men), in particular the **~14% for the running leg**.
    - Probably all athletes **run slower** during T1 compared to the subsequent 5k or 10k. For diverse reasons:
      - They are **barefoot**.
      - Their hands are occupied with **swim gear or pushing the bike**.
      - The course often **includes stairs**, e.g. [at Pont Alexandre III during the 2024 Paris Olympics ( :fr: )](https://youtu.be/bXIAfVppavI?t=1920), or sharp turns.
    - Probably the **decrease in running speed** is more important for men, leading to a lower gender difference.
- Finally, while these estimates **focus on time**, the wetsuit also **provides energy savings** (e.g. buoyancy and warmth), as discussed in the section _[Is the wetsuit worth for 300m?](#is-the-wetsuit-worth-for-300m)_.

---

# :dart: RACE SCENARIO

This section looks at the race dynamics of **WCTS and games-related events** (no world-cup).
- Based on the information **_"does a bunch manage to breakaway on the bike?"_** :bird:

To obtain this information, the **size** of the **front pack** at the **end of the bike** is estimated as follows:
- Compute, for each athlete, the cumulative times after the bike:
  - `start_to_t2 = swim + t1 + bike`.
- Identify which athlete enters T2 first: `min(start_to_t2)`.
- Count how many athletes enter T2 **`pack_duration_s`, e.g. 10s, or less** after this first athlete.
- This gives the **size of the front pack** at the **end of the bike**.

Note: A **breakaway** on the bike can happen:
- Either by **attack and escape from the main bike pack** (rare).
- Or **directly from the swim** (most common).
- It should be possible to automatically retrieve the **breakaway type** among the two, using the swim rank of athletes composing the breakaway. _(I have not done it)_.

Two additional pieces of information are retrieved:
- :trophy: **`winner_in_front_pack`**: was the **winner already in the leading group** at the end of the bike, or did she/he **come back on the run**?
- :athletic_shoe: **`is_best_runner_in_front_pack`**.

|       ![scenarios.png](res/scenarios.png)        | 
|:------------------------------------------------:| 
| *Size of the front pack at the end of the bike.* |

About the **number of finishers**:
- **~4.5 more** finishers in **men's** races.
  - The standard deviation is higher for women's race.
- **~3.5** more** finishers in **sprint format** races.
  - Because the olympic format is longer, weaker athletes are more likely to be caught and eliminated by being lapped?
- It would be interesting to know the **number of starters** as well.

On the **olympic** format, **men are more likely to break away**.
- Because they are stronger on the bike?
  - Georgia Taylor-Brown ( :gb: ), **one of the strongest rider** in the field, admits in [this video](https://youtu.be/8dvcwuT2T_8?t=1251): **_"I would love to be able to attack and stay away, but I do not have that power."_**
  - Probably bike is the sport among three where **top athletes will progress the most** in the future.
- At the same time, the **probability to win** for athletes from the front group is **much lower for men than for women**.

Small front packs, i.e. **small breakaways**, are more likely on the **olympic format**.
- Possibly because a **longer swim** leads to **larger gaps** at **T1**?
- On the other hand the bike is longer than for the sprint format, which **should give more time** for the other packs to catch up. 

---

Some **very large front groups** at T2 (London ( :gb: ) at the top :guard: ):

|  **PACK_SIZE**  |  YEAR  |             WINNER              |  DISTANCE  |  CAT  |                                                                                                          EVENT                                                                                                           |
|:---------------:|:------:|:-------------------------------:|:----------:|:-----:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|     **53**      |  2011  |     Helen Jenkins ( :gb: )      |  OLYMPIC   | WTCS  |                [2011 Dextro Energy Triathlon - ITU World Championship Series London ( :gb: )](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london)                |
|     **46**      |  2012  |  Erin Densham ( :australia: )   |  OLYMPIC   | WTCS  |                                           [2012 Dextro Energy World Triathlon Sydney ( :australia: )](https://www.triathlon.org/events/event/2012_itu_world_triathlon_sydney)                                            |
|     **39**      |  2011  |   Paula Findlay ( :canada: )    |  OLYMPIC   | WTCS  |            [2011 Dextro Energy Triathlon - ITU World Championship Series Sydney ( :australia: )](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_sydney)             |
|     **39**      |  2011  | Andrea Hansen ( :new_zealand: ) |  OLYMPIC   | WTCS  |              [2011 Dextro Energy Triathlon - ITU World Championship Series Yokohama ( :jp: )](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_yokohama)              |
|     **37**      |  2012  | Nicola Spirig ( :switzerland: ) |  OLYMPIC   | WTCS  |                                                    [2012 ITU World Triathlon Madrid ( :es: )](https://www.triathlon.org/events/event/2012_itu_world_triathlon_madrid)                                                    |
|      *...*      |  ...   |               ...               |    ...     |  ...  |                                                                                                           ...                                                                                                            |
|     **52**      |  2014  |       Mario Mola ( :es: )       |   SPRINT   | WTCS  |                                                    [2014 ITU World Triathlon London ( :gb: )](https://www.triathlon.org/events/event/2014_itu_world_triathlon_london)                                                    |
|     **51**      |  2023  |        Alex Yee ( :gb: )        |  OLYMPIC   | GAMES |                                       [2023 World Triathlon Olympic Games Test Event Paris ( :fr: )](https://www.triathlon.org/events/event/2023_world_triathlon_test_event_paris)                                       |
|     **49**      |  2023  |        Alex Yee ( :gb: )        |   SPRINT   | WTCS  |                        [2023 World Triathlon Championship Series Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_abu_dhabi)                        |
|     **46**      |  2016  |       Mario Mola ( :es: )       |  OLYMPIC   | WTCS  |                                                  [2016 ITU World Triathlon Yokohama ( :jp: )](https://www.triathlon.org/events/event/2016_itu_world_triathlon_yokohama)                                                  |
|     **45**      |  2011  | Brad Kahlefeldt ( :australia: ) |  OLYMPIC   | WTCS  |               [2011 Dextro Energy Triathlon - ITU World Championship Series Hamburg ( :de: )](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_hamburg)               |

---

<details>
  <summary>Click to expand - :muscle: <strong>Some wins via breakaway (with front-pack-size <= 3).</strong></summary>

|  **PACK_SIZE**  |  YEAR  |               WINNER                |  DISTANCE  |    CAT    |                                                                                                 EVENT                                                                                                  |
|:---------------:|:------:|:-----------------------------------:|:----------:|:---------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|      **1**      |  2011  |       Sarah Haskins ( :us: )        |  OLYMPIC   | WORLD-CUP |                                  [2011 Monterrey ITU Triathlon World Cup ( :mexico: )](https://www.triathlon.org/events/event/2011_monterrey_itu_triathlon_world_cup)                                  |
|      **1**      |  2016  |      Flora Duffy ( :bermuda: )      |  OLYMPIC   |   WTCS    |                                      [2016 ITU World Triathlon Stockholm ( :sweden: )](https://www.triathlon.org/events/event/2016_itu_world_triathlon_stockholm)                                      |
|      **1**      |  2018  |      Flora Duffy ( :bermuda: )      |  OLYMPIC   |   WTCS    |                                       [2018 ITU World Triathlon Bermuda ( :bermuda: )](https://www.triathlon.org/events/event/2018_itu_world_triathlon_bermuda)                                        |
|      **1**      |  2021  |        Taylor Knibb ( :us: )        |  OLYMPIC   |   WTCS    |                           [2021 World Triathlon Championship Finals Edmonton ( :canada: )](https://www.triathlon.org/events/event/2021_world_triathlon_grand_final_edmonton)                           |
|      **2**      |  2011  |   Nicky Samuels ( :new_zealand: )   |  OLYMPIC   | WORLD-CUP |                               [2011 Mooloolaba ITU Triathlon World Cup ( :australia: )](https://www.triathlon.org/events/event/2011_mooloolaba_itu_triathlon_world_cup)                                |
|      **2**      |  2017  |      Flora Duffy ( :bermuda: )      |  OLYMPIC   |   WTCS    |                                         [2017 ITU World Triathlon Yokohama ( :jp: )](https://www.triathlon.org/events/event/2017_itu_world_triathlon_yokohama)                                         |
|      **2**      |  2021  |        Taylor Knibb ( :us: )        |  OLYMPIC   |   WTCS    |                                   [2021 World Triathlon Championship Series Yokohama ( :jp: )](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama)                                   |
|      **2**      |  2022  |      Flora Duffy ( :bermuda: )      |  OLYMPIC   |   WTCS    |                       [2022 World Triathlon Championship Series Bermuda ( :bermuda: )](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_bermuda)                        |
|      **3**      |  2009  |    Emma Moffatt ( :australia: )     |  OLYMPIC   |   WTCS    |      [2009 Dextro Energy Triathlon - ITU World Championship Series Hamburg ( :de: )](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_hamburg)      |
|      **3**      |  2014  |       Jodie Stimpson ( :gb: )       |  OLYMPIC   |   WTCS    |                                    [2014 ITU World Triathlon Auckland ( :new_zealand: )](https://www.triathlon.org/events/event/2014_itu_world_triathlon_auckland)                                     |
|      **3**      |  2016  |       Helen Jenkins ( :gb: )        |  OLYMPIC   |   WTCS    |                                   [2016 ITU World Triathlon Gold Coast ( :australia: )](https://www.triathlon.org/events/event/2016_itu_world_triathlon_gold_coast)                                    |
|      **3**      |  2016  |      Flora Duffy ( :bermuda: )      |  OLYMPIC   |   WTCS    |                            [2016 ITU World Triathlon Grand Final Cozumel ( :mexico: )](https://www.triathlon.org/events/event/2016_itu_world_triathlon_grand_final_cozumel)                            |
|      **3**      |  2017  |      Flora Duffy ( :bermuda: )      |  OLYMPIC   |   WTCS    |                       [2017 ITU World Triathlon Grand Final Rotterdam ( :netherlands: )](https://www.triathlon.org/events/event/2017_itu_world_triathlon_grand_final_rotterdam)                        |
|      **3**      |  2019  |       Katie Zaferes ( :us: )        |  OLYMPIC   |   WTCS    |                                  [2019 MS Amlin World Triathlon Bermuda ( :bermuda: )](https://www.triathlon.org/events/event/2019_ms_amlin_world_triathlon_bermuda)                                   |
|      **3**      |  2019  |   Julie Derron ( :switzerland: )    |  OLYMPIC   | WORLD-CUP |                                       [2019 Weihai ITU Triathlon World Cup ( :cn: )](https://www.triathlon.org/events/event/2019_weihai_itu_triathlon_world_cup)                                       |
|      **3**      |  2021  |    Maya Kingma ( :netherlands: )    |  OLYMPIC   |   WTCS    |                                  [AJ Bell 2021 World Triathlon Championship Series Leeds ( :gb: )](https://www.triathlon.org/events/event/2021_world_triathlon_leeds)                                  |
|      **3**      |  2024  |        Lena Meißner ( :de: )        |  OLYMPIC   | WORLD-CUP |                                    [2024 World Triathlon Cup Samarkand ( :uzbekistan: )](https://www.triathlon.org/events/event/2024_world_triathlon_cup_samarkand)                                    |
|       ...       |  ...   |                 ...                 |    ...     |    ...    |                                                                                                  ...                                                                                                   |
|      **1**      |  2013  |     Alistair Brownlee ( :gb: )      |  OLYMPIC   |   WTCS    |                                      [2013 ITU World Triathlon Stockholm ( :sweden: )](https://www.triathlon.org/events/event/2013_itu_world_triathlon_stockholm)                                      |
|      **1**      |  2018  |     Casper Stornes ( :norway: )     |  OLYMPIC   |   WTCS    |                                       [2018 ITU World Triathlon Bermuda ( :bermuda: )](https://www.triathlon.org/events/event/2018_itu_world_triathlon_bermuda)                                        |
|      **1**      |  2023  |       Morgan Pearson ( :us: )       |  OLYMPIC   | WORLD-CUP |                               [2023 World Triathlon Cup Karlovy Vary ( :czech_republic: )](https://www.triathlon.org/events/event/2023_world_triathlon_cup_karlovy_vary)                               |
|      **2**      |  2011  |   Kris Gemmell ( :new_zealand: )    |  OLYMPIC   | WORLD-CUP |                                [2011 Auckland ITU Triathlon World Cup ( :new_zealand: )](https://www.triathlon.org/events/event/2011_auckland_itu_triathlon_world_cup)                                 |
|      **2**      |  2016  | Rodrigo Gonzalez Lopez ( :mexico: ) |  OLYMPIC   | WORLD-CUP |                                      [2016 Chengdu ITU Triathlon World Cup ( :cn: )](https://www.triathlon.org/events/event/2016_chengdu_itu_triathlon_world_cup)                                      |
|      **3**      |  2009  |        Jan Frodeno ( :de: )         |  OLYMPIC   |   WTCS    |     [2009 Dextro Energy Triathlon - ITU World Championship Series Yokohama ( :jp: )](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_yokohama)     |
|      **3**      |  2011  |     Alistair Brownlee ( :gb: )      |  OLYMPIC   |   WTCS    | [2011 Dextro Energy Triathlon - ITU World Championship Series Kitzbuehel ( :austria: )](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_kitzbuhel) |
|      **3**      |  2014  |     Alistair Brownlee ( :gb: )      |  OLYMPIC   |   WTCS    |                           [2014 ITU World Triathlon Grand Final Edmonton ( :canada: )](https://www.triathlon.org/events/event/2014_itu_world_triathlon_grand_final_edmonton)                           |
|      **3**      |  2015  |     Jonathan Brownlee ( :gb: )      |  OLYMPIC   |   WTCS    |                                   [2015 ITU World Triathlon Gold Coast ( :australia: )](https://www.triathlon.org/events/event/2015_itu_world_triathlon_gold_coast)                                    |
|      **3**      |  2020  |        Vincent Luis ( :fr: )        |  OLYMPIC   | WORLD-CUP |                           [2020 Karlovy Vary ITU Triathlon World Cup ( :czech_republic: )](https://www.triathlon.org/events/event/2020_karlovy_vary_itu_triathlon_world_cup)                           |

Strong bikers and **very versatile** triathletes! :clap:
- Especially **Flora Duffy** ( :bermuda: ) and **Alistair Brownlee** ( :gb: ).

</details>

---

Below is a more complicated figure: the bars show the evolution of the average **first-pack size** over the years.

| ![scenarios_over_years.png](res/scenarios_over_years.png) | 
|:---------------------------------------------------------:| 
|        *Size of front bike pack, over the years.*         |

**Run-comebacks**, i.e. winning after not being in the front group after bike, are **rare**.
- Apart from 2013-2016 (the era of Gwen Jorgensen ( :us: )), **no comeback has happened on women's olympic races** and only a few on women's sprint format.
  - At the same time, the size of **front-pack had reduced until 2022** and was even very small for some recent years (2017, 2019, 2021, 2022).
  - Now, **top-women-swimmer** can **ride hard** and **run fast**.
- Helen Jenkins ( :gb: ) explains in [this 2024 video](https://youtu.be/QwCUmvPCjw4?t=338): _"Women's races have definitely changed over the past few years. (...) **2021 was that breakaway era**. It definitely **comes back** to that **larger front group** over the last couple of years."_
  - That statement is perfectly **consistent** with the women's olympic bar plot.
- The **men's olympic races** follow a similar same trend: the **front group at T2 has, on average, never been as large**, as in 2023 and 2024.

---

### :runner: How often does the best runner win? :trophy:

| ![best_runner_wins.png](res/best_runner_wins.png) | 
|:-------------------------------------------------:| 
|       *How often does the best runner win?*       |

More than **2/3 races** are **won by the best runner**.
- This percentage is higher on the **sprint** than on the **olympic** format.
  - Probably because the swim is shorter: "good-runner-but-bad-swimmer"s are **less likely to miss the front group** on the bike.
- This percentage could be:
  - Higher, if the winner does not slow down and **"enjoy" the last 100m run**, and instead sprints until the end, as most athletes behind have to. Example: [Leonie Periault ( :fr: )](https://youtu.be/XMa5Soyx498?t=209) in [2024 Yokohama ( :jp: )](https://triathlon.org/results/result/2023_world_triathlon_championship_series_yokohama1/627955).
  - Lower, if good runners who, at T2, are already too far for the win, **get as motivated** as the athletes at the front, and give their best possible run.
- The percentage **drops to 50%** when considering **world-cup** events only. Why?
  - Because athletes are **not as complete as on WTCS**?
  - There are **more "good-runner-but-bad-swimmer"s** who miss the front group on the bike, while good swimmers are not top runners?

<details>
  <summary>Click to expand - <strong>Same plots for world-cup events only.</strong></summary>

|       ![scenarios.png](res/scenarios.png)        | 
|:------------------------------------------------:| 
| *Size of the front pack at the end of the bike.* |

| ![scenarios_over_years.png](res/scenarios_over_years_wc.png) | 
|:------------------------------------------------------------:| 
|          *Size of front bike pack, over the years.*          |

| ![best_runner_wins_wc.png](res/best_runner_wins_wc.png) | 
|:-------------------------------------------------------:| 
|         *How often does the best runner wins?*          |

</details>

---

Why are there not **more breakaways** on the bike?
- The **mini areo TT bars** [have been banned](https://www.slowtwitch.com/Lifestyle/An_Athlete_s_Perspective_on_2022_World_Triathlon_Rules_8217.html) in 2023.
- Bike courses are **mostly flat**.
  - Events often take place on flat coasts, near to a sea, or in **flat big cities**.
  - [Joel Filliol](https://joelfilliol.com/) ( :canada: :scotland: ) shares insights in [this TTS podcast (around 43:00)](https://scientifictriathlon.com/tts409/) about bike courses that allow for a break to stay away.
- Because of **U-turns**.
  - As Michel Hidalgo ( :brazil: ) [explains in this video](https://youtu.be/8dvcwuT2T_8?t=780), **U-turns can be detrimental for breakaways**.
- Athletes may prefer to conserve energy for the **run segment**.
  - Valid of strong runners.
  - But for others? Maybe it is **worth more** to **conserve energy by drafting** and try to make top-20 with a good run, rather than risk a breakaway that might be caught, be burnt and **come back home without any prize money or qualification points**?
- Not enough bike power?
  - Possibly, given these athletes need to be strong in swim and run as well, they cannot **afford having massive legs**.

---

---

# :rocket: SPRINT FINISH

This section studies the **time gap between the winner and the second**.

|  ![sprint_finish.png](res/sprint_finish.png)  | 
|:---------------------------------------------:| 
| *Time gap between the winner and the second.* |

- In men's races, **17%** (sprint format) and **10%** (olympic) are **won by a sprint finish**, occurring **50% more often** than in women's races.
- Women's races offer **examples of wins by very large margins**.

|                                                   ![sprint_finish_over_years.png](res/sprint_finish_over_years.png)                                                    | 
|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------:| 
| *Time gap between the winner and the second, over years. And the proportion of events with a contested win finish (less than 3s difference between first and second).* |

Gaps **between the winner and the second** are on average:
- **~Twice as large** in **olympic** formats compared to **sprint** formats.
- **~Twice as large** for **women** compared to **men**.

It has been a long time since a **women's olympic race** was won by a **sprint**.

---

<details>
  <summary>Click to expand - 📸 <strong>Some of the most contested finishes on the blue carpet.</strong></summary>

##### WOMEN

|                                                        YEAR                                                         |                                                                VENUE                                                                 |  DIST.  | RACE CATEGORY |      FIRST ( :1st_place_medal: )      |         SECOND ( :2nd_place_medal: )         |
|:-------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------:|:-------:|:-------------:|:-------------------------------------:|:--------------------------------------------:|
| [2009](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_madrid1) |    [Madrid](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_madrid1) ( :es: )    | olympic |     WTCS      |    Andrea Hansen ( :new_zealand: )    |           Lisa Norden ( :sweden: )           |
| [2010](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) |   [Hamburg](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )    | olympic |     WTCS      |       Lisa Norden ( :sweden: )        |         Emma Moffatt ( :australia: )         |
| [2010](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_sydney)  | [Sydney](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_sydney) ( :australia: ) | olympic |     WTCS      |      Barbara Riveros ( :chile: )      |       Andrea Hansen ( :new_zealand: )        |
|              [2010](https://www.triathlon.org/events/event/2010_tiszaujvaros_itu_triathlon_world_cup)               |            [Tiszaujvaros](https://www.triathlon.org/events/event/2010_tiszaujvaros_itu_triathlon_world_cup) ( :hungary: )            | olympic |   world-cup   |   Yuliya Yelistratova ( :ukraine: )   |            Jodie Swallow ( :gb: )            |
|     [2011](https://www.triathlon.org/events/event/2011_lausanne_itu_elite_sprint_triathlon_world_championships)     |  [Lausanne](https://www.triathlon.org/events/event/2011_lausanne_itu_elite_sprint_triathlon_world_championships) ( :switzerland: )   | sprint  |     WTCS      |      Barbara Riveros ( :chile: )      |         Emma Jackson ( :australia: )         |
|                  [2012](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama)                   |                    [Yokohama](https://www.triathlon.org/events/event/2012_itu_world_triathlon_yokohama) ( :jp: )                     | olympic |     WTCS      |       Lisa Norden ( :sweden: )        |              Anne Haug ( :de: )              |
|                      [2012](https://www.triathlon.org/events/event/2012_london_olympic_games)                       |                         [London](https://www.triathlon.org/events/event/2012_london_olympic_games) ( :gb: )                          | olympic |     games     |    Nicola Spirig ( :switzerland: )    |           Lisa Norden ( :sweden: )           |
|              [2015](https://www.triathlon.org/events/event/2015_tiszaujvaros_itu_triathlon_world_cup)               |            [Tiszaujvaros](https://www.triathlon.org/events/event/2015_tiszaujvaros_itu_triathlon_world_cup) ( :hungary: )            | sprint  |   world-cup   | Felicity Sheedy-Ryan ( :australia: )  |            Audrey Merle ( :fr: )             |
|                [2017](https://www.triathlon.org/events/event/2017_cape_town_itu_triathlon_world_cup)                |            [Cape Town](https://www.triathlon.org/events/event/2017_cape_town_itu_triathlon_world_cup) ( :south_africa: )             | sprint  |   world-cup   |       Lucy Buckingham ( :gb: )        |          Jessica Learmonth ( :gb: )          |
|                  [2017](https://www.triathlon.org/events/event/2017_itu_world_triathlon_abu_dhabi)                  |          [Abu Dhabi](https://www.triathlon.org/events/event/2017_itu_world_triathlon_abu_dhabi) ( :united_arab_emirates: )           | olympic |     WTCS      |    Andrea Hansen ( :new_zealand: )    |           Jodie Stimpson ( :gb: )            |
|              [2017](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup)               |          [New Plymouth](https://www.triathlon.org/events/event/2017_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )          | sprint  |   world-cup   |        Katie Zaferes ( :us: )         |          Joanna Brown ( :canada: )           |
|                [2018](https://www.triathlon.org/events/event/2018_cagliari_itu_triathlon_world_cup)                 |                  [Cagliari](https://www.triathlon.org/events/event/2018_cagliari_itu_triathlon_world_cup) ( :it: )                   | sprint  |   world-cup   |      Lisa Perterer ( :austria: )      |            Taylor Spivey ( :us: )            |
|              [2018](https://www.triathlon.org/events/event/2018_karlovy_vary_itu_triathlon_world_cup)               |        [Karlovy Vary](https://www.triathlon.org/events/event/2018_karlovy_vary_itu_triathlon_world_cup) ( :czech_republic: )         | olympic |   world-cup   | Vendula Frintova ( :czech_republic: ) |         Kaidi Kivioja ( :estonia: )          |
|                 [2019](https://www.triathlon.org/events/event/2019_madrid_itu_triathlon_world_cup)                  |                    [Madrid](https://www.triathlon.org/events/event/2019_madrid_itu_triathlon_world_cup) ( :es: )                     | sprint  |   world-cup   |        Emilie Morier ( :fr: )         |            Sandra Dodet ( :fr: )             |
|              [2019](https://www.triathlon.org/events/event/2019_tiszaujvaros_itu_triathlon_world_cup)               |           [Tiszaujvaros ](https://www.triathlon.org/events/event/2019_tiszaujvaros_itu_triathlon_world_cup) ( :hungary: )            | sprint  |   world-cup   |     Emma Jeffcoat ( :australia: )     |           Sara Vilic ( :austria: )           |
|                   [2022](https://www.triathlon.org/events/event/2022_world_triathlon_cup_bergen)                    |                    [Bergen](https://www.triathlon.org/events/event/2022_world_triathlon_cup_bergen) ( :norway: )                     | sprint  |   world-cup   |      Tilda Månsson ( :sweden: )       |        Jolien Vermeylen ( :belgium: )        |
|                [2023](https://www.triathlon.org/events/event/2023_world_triathlon_cup_tiszaujvaros)                 |              [Tiszaujvaros](https://www.triathlon.org/events/event/2023_world_triathlon_cup_tiszaujvaros) ( :hungary: )              | sprint  |   world-cup   |      Tilda Månsson ( :sweden: )       |             Noelia Juan ( :es: )             |
|                  [2024](https://www.triathlon.org/events/event/2024_world_triathlon_cup_huatulco)                   |                  [Huatulco](https://www.triathlon.org/events/event/2024_world_triathlon_cup_huatulco) ( :mexico: )                   | sprint  |   world-cup   |  Alberte Kjær Pedersen ( :denmark: )  |       Rachel Klamer ( :netherlands: )        |
|                 [2024](https://www.triathlon.org/events/event/2024_world_triathlon_cup_wollongong)                  |               [Wollongong](https://www.triathlon.org/events/event/2024_world_triathlon_cup_wollongong) ( :australia: )               | sprint  |   world-cup   |      Tilda Månsson ( :sweden: )       | Maria Carolina Velasquez Soto ( :colombia: ) |

##### MEN

|                                                         YEAR                                                          |                                                                VENUE                                                                |  DIST.  | RACE CATEGORY |    FIRST ( :1st_place_medal: )    |    SECOND ( :2nd_place_medal: )    |
|:---------------------------------------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------:|:-------:|:-------------:|:---------------------------------:|:----------------------------------:|
| [2009](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_tongyeong) | [Tongyeong](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_tongyeong) ( :kr: ) | olympic |     WTCS      | Bevan Docherty ( :new_zealand: )  |  Brad Kahlefeldt ( :australia: )   |
|                  [2009](https://www.triathlon.org/events/event/2009_hy-vee_itu_triathlon_elite_cup)                   |                  [Des Moines](https://www.triathlon.org/events/event/2009_hy-vee_itu_triathlon_elite_cup) ( :us: )                  | olympic |   world-cup   |   Simon Whitfield ( :canada: )    |  Brad Kahlefeldt ( :australia: )   |
|   [2010](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_seoul)   |     [Seoul](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_seoul) ( :kr: )     | olympic |     WTCS      |       Jan Frodeno ( :de: )        | Courtney Atkinson ( :australia: )  |
|  [2011](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_hamburg)  |   [Hamburg](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_hamburg) ( :de: )   | olympic |     WTCS      |  Brad Kahlefeldt ( :australia: )  |      William Clarke ( :gb: )       |
|                [2012](https://www.triathlon.org/events/event/2012_mooloolaba_itu_triathlon_world_cup)                 |            [Mooloolaba](https://www.triathlon.org/events/event/2012_mooloolaba_itu_triathlon_world_cup) ( :australia: )             | olympic |   world-cup   |      Laurent Vidal ( :fr: )       |  Brad Kahlefeldt ( :australia: )   |
|              [2013](https://www.triathlon.org/events/event/2013_itu_world_triathlon_grand_final_london)               |                [London](https://www.triathlon.org/events/event/2013_itu_world_triathlon_grand_final_london) ( :gb: )                | olympic |     WTCS      |    Javier Gomez Noya ( :es: )     |     Jonathan Brownlee ( :gb: )     |
|                    [2013](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg)                    |                     [Hamburg](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                     | sprint  |     WTCS      |    Jonathan Brownlee ( :gb: )     |     Alistair Brownlee ( :gb: )     |
|                  [2014](https://www.triathlon.org/events/event/2014_chengdu_itu_triathlon_world_cup)                  |                   [Chengdu](https://www.triathlon.org/events/event/2014_chengdu_itu_triathlon_world_cup) ( :cn: )                   | olympic |   world-cup   | Wian Sullwald ( :south_africa: )  |      Kevin McDowell ( :us: )       |
|                    [2014](https://www.triathlon.org/events/event/2014_itu_world_triathlon_london)                     |                      [London](https://www.triathlon.org/events/event/2014_itu_world_triathlon_london) ( :gb: )                      | sprint  |     WTCS      |        Mario Mola ( :es: )        | Richard Murray ( :south_africa: )  |
|                   [2014](https://www.triathlon.org/events/event/2014_itu_world_triathlon_yokohama)                    |                    [Yokohama](https://www.triathlon.org/events/event/2014_itu_world_triathlon_yokohama) ( :jp: )                    | olympic |     WTCS      |    Javier Gomez Noya ( :es: )     |        Mario Mola ( :es: )         |
|               [2014](https://www.triathlon.org/events/event/2014_tiszaujvaros_itu_triathlon_world_cup)                |           [Tiszaujvaros](https://www.triathlon.org/events/event/2014_tiszaujvaros_itu_triathlon_world_cup) ( :hungary: )            | sprint  |   world-cup   |     Ákos Vanek ( :hungary: )      | Rostislav Pevtsov ( :azerbaijan: ) |
|                  [2015](https://www.triathlon.org/events/event/2015_chengdu_itu_triathlon_world_cup)                  |                   [Chengdu](https://www.triathlon.org/events/event/2015_chengdu_itu_triathlon_world_cup) ( :cn: )                   | olympic |   world-cup   |    Ryan Fisher ( :australia: )    | Rostislav Pevtsov ( :azerbaijan: ) |
|                 [2016](https://www.triathlon.org/events/event/2016_miyazaki_itu_triathlon_world_cup)                  |                  [Miyazaki](https://www.triathlon.org/events/event/2016_miyazaki_itu_triathlon_world_cup) ( :jp: )                  | olympic |   world-cup   |     Uxio Abuin Ares ( :es: )      |     Joao Silva ( :portugal: )      |
|                  [2016](https://www.triathlon.org/events/event/2016_salinas_itu_triathlon_world_cup)                  |                [Salinas](https://www.triathlon.org/events/event/2016_salinas_itu_triathlon_world_cup) ( :ecuador: )                 | sprint  |   world-cup   |   David Castro Fajardo ( :es: )   |      Matthew McElroy ( :us: )      |
|                 [2016](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup)                 |                 [Tongyeong](https://www.triathlon.org/events/event/2016_tongyeong_itu_triathlon_world_cup) ( :kr: )                 | sprint  |   world-cup   |     Uxio Abuin Ares ( :es: )      |      Matthew McElroy ( :us: )      |
|                 [2018](https://www.triathlon.org/events/event/2018_tongyeong_itu_triathlon_world_cup)                 |                 [Tongyeong](https://www.triathlon.org/events/event/2018_tongyeong_itu_triathlon_world_cup) ( :kr: )                 | sprint  |   world-cup   |   Max Studer ( :switzerland: )    |    Felix Duchampt ( :romania: )    |
|                 [2019](https://www.triathlon.org/events/event/2019_cagliari_itu_triathlon_world_cup)                  |                  [Cagliari](https://www.triathlon.org/events/event/2019_cagliari_itu_triathlon_world_cup) ( :it: )                  | sprint  |   world-cup   |    Alistair Brownlee ( :gb: )     |     Justus Nieschlag ( :de: )      |
|                  [2019](https://www.triathlon.org/events/event/2019_hamburg_wasser_world_triathlon)                   |                   [Hamburg](https://www.triathlon.org/events/event/2019_hamburg_wasser_world_triathlon) ( :de: )                    | sprint  |     WTCS      | Jacob Birtwhistle ( :australia: ) |       Vincent Luis ( :fr: )        |
|                   [2019](https://www.triathlon.org/events/event/2019_itu_world_triathlon_montreal)                    |                  [Montreal](https://www.triathlon.org/events/event/2019_itu_world_triathlon_montreal) ( :canada: )                  | sprint  |     WTCS      |     Jelle Geens ( :belgium: )     |        Mario Mola ( :es: )         |
|                  [2019](https://www.triathlon.org/events/event/2019_madrid_itu_triathlon_world_cup)                   |                    [Madrid](https://www.triathlon.org/events/event/2019_madrid_itu_triathlon_world_cup) ( :es: )                    | sprint  |   world-cup   |     Justus Nieschlag ( :de: )     |        Lasse Lührs ( :de: )        |
|               [2019](https://www.triathlon.org/events/event/2019_tiszaujvaros_itu_triathlon_world_cup)                |           [Tiszaujvaros ](https://www.triathlon.org/events/event/2019_tiszaujvaros_itu_triathlon_world_cup) ( :hungary: )           | sprint  |   world-cup   |       Eli Hemming ( :us: )        |    Ryan Fisher ( :australia: )     |
|                [2020](https://www.triathlon.org/events/event/2020_mooloolaba_itu_triathlon_world_cup)                 |            [Mooloolaba](https://www.triathlon.org/events/event/2020_mooloolaba_itu_triathlon_world_cup) ( :australia: )             | sprint  |   world-cup   |  Ryan Sissons ( :new_zealand: )   |   Hayden Wilde ( :new_zealand: )   |
|               [2021](https://www.triathlon.org/events/event/2021_world_triathlon_grand_final_edmonton)                |              [Edmonton](https://www.triathlon.org/events/event/2021_world_triathlon_grand_final_edmonton) ( :canada: )              | olympic |     WTCS      | Kristian Blummenfelt ( :norway: ) |   Marten Van Riel ( :belgium: )    |
|                      [2021](https://www.triathlon.org/events/event/2021_world_triathlon_hamburg)                      |                       [Hamburg](https://www.triathlon.org/events/event/2021_world_triathlon_hamburg) ( :de: )                       | sprint  |     WTCS      |       Tim Hellwig ( :de: )        |     Paul Georgenthum ( :fr: )      |
|                    [2022](https://www.triathlon.org/events/event/2022_world_triathlon_cup_bergen)                     |                    [Bergen](https://www.triathlon.org/events/event/2022_world_triathlon_cup_bergen) ( :norway: )                    | sprint  |   world-cup   |      Dorian Coninx ( :fr: )       | Kristian Blummenfelt ( :norway: )  |
|                   [2022](https://www.triathlon.org/events/event/2022_world_triathlon_cup_huatulco)                    |                  [Huatulco](https://www.triathlon.org/events/event/2022_world_triathlon_cup_huatulco) ( :mexico: )                  | sprint  |   world-cup   |        Genis Grau ( :es: )        |   Tyler Mislawchuk ( :canada: )    |
|          [2023](https://www.triathlon.org/events/event/2023_world_triathlon_championship_finals_pontevedra)           |          [Pontevedra](https://www.triathlon.org/events/event/2023_world_triathlon_championship_finals_pontevedra) ( :es: )          | olympic |     WTCS      |      Dorian Coninx ( :fr: )       |        Tim Hellwig ( :de: )        |
|          [2023](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_sunderland)           |          [Sunderland](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_sunderland) ( :gb: )          | sprint  |     WTCS      |     Pierre Le Corre ( :fr: )      |        Léo Bergere ( :fr: )        |
|                   [2023](https://www.triathlon.org/events/event/2023_world_triathlon_cup_huatulco)                    |                  [Huatulco](https://www.triathlon.org/events/event/2023_world_triathlon_cup_huatulco) ( :mexico: )                  | sprint  |   world-cup   |   David Castro Fajardo ( :es: )   |   Tyler Mislawchuk ( :canada: )    |
|                   [2023](https://www.triathlon.org/events/event/2023_world_triathlon_cup_valencia)                    |                    [Valencia](https://www.triathlon.org/events/event/2023_world_triathlon_cup_valencia) ( :es: )                    | olympic |   world-cup   | David Cantero Del Campo ( :es: )  |  Lasse Nygaard Priester ( :de: )   |

Not many highly contested finishes on **women's world-series** for a while!

</details>

---

By the way, [World Triathlon rules](https://www.triathlon.org/uploads/docs/World-Triathlon_Competition-Rules_2024_20240416.pdf) that the **win must be contested**:
- Triathletes **should not** _"finish in a **contrived tie situation where no effort** to separate the finish times has been made"._
- At Tokyo ( :jp: ) 2019, Jessica Learmonth ( :gb: ) and Georgia Taylor-Brown ( :gb: ) were **[disqualified after crossing line hand-in-hand](https://www.theguardian.com/sport/2019/aug/15/winning-triathletes-jess-learmonth-georgia-taylor-brown-disqualified-tokyo-hand-in-hand-triathlon)**.

---

---

# :spiral_calendar: LEVEL OVER YEARS

The same **outlier removal** is applied as described in the [:stopwatch: PACES section](#stopwatch-paces).

| ![repeated_events_standard_w.png](res/repeated_events_standard_w.png) | 
|:---------------------------------------------------------------------:| 
|                       *Olympic format. Women.*                        |

| ![repeated_events_standard_m.png](res/repeated_events_standard_m.png) | 
|:---------------------------------------------------------------------:| 
|                        *Olympic format. Men.*                         |

---

<details>
  <summary>Click to expand - 🚀 <strong>Same plots for the Sprint format.</strong></summary>

| ![repeated_events_sprint_w.png](res/repeated_events_sprint_w.png) | 
|:-----------------------------------------------------------------:| 
|                      *Sprint format. Women.*                      |

| ![repeated_events_sprint_m.png](res/repeated_events_sprint_m.png) | 
|:-----------------------------------------------------------------:| 
|                       *Sprint format. Men.*                       |

</details>

---

<details>
  <summary>Click to expand - 🏅 <strong>Same plots for the Top-3.</strong></summary>

| ![repeated_events_standard_w_top3.png](res/repeated_events_standard_w_top3.png) | 
|:-------------------------------------------------------------------------------:| 
|                   *Olympic format. Top-3 women in each leg.*                    |

| ![repeated_events_standard_w_top3.png](res/repeated_events_standard_m_top3.png) | 
|:-------------------------------------------------------------------------------:| 
|                    *Olympic format. Top-3 men in each leg.*                     |

| ![repeated_events_sprint_w_top3.png](res/repeated_events_sprint_w_top3.png) | 
|:---------------------------------------------------------------------------:| 
|                  *Sprint format. Top-3 women in each leg.*                  |

| ![repeated_events_sprint_w_top3.png](res/repeated_events_sprint_m_top3.png) | 
|:---------------------------------------------------------------------------:| 
|                   *Sprint format. Top-3 men in each leg.*                   |

</details>

---

<details>
  <summary>Click to expand - 🏁 <strong>Same plots for the Top-10.</strong></summary>

| ![repeated_events_standard_w_top10.png](res/repeated_events_standard_w_top10.png) | 
|:---------------------------------------------------------------------------------:| 
|                    *Olympic format. Top-10 women in each leg.*                    |

| ![repeated_events_standard_w_top10.png](res/repeated_events_standard_m_top10.png) | 
|:---------------------------------------------------------------------------------:| 
|                     *Olympic format. Top-10 men in each leg.*                     |

| ![repeated_events_sprint_w_top10.png](res/repeated_events_sprint_w_top10.png) | 
|:-----------------------------------------------------------------------------:| 
|                  *Sprint format. Top-10 women in each leg.*                   |

| ![repeated_events_sprint_w_top10.png](res/repeated_events_sprint_m_top10.png) | 
|:-----------------------------------------------------------------------------:| 
|                   *Sprint format. Top-10 men in each leg.*                    |

</details>

---

In [this early-2024 video](https://youtu.be/iCpi2sUh6Ko?t=1838), **Vincent Luis** ( :fr: ) explains:

> "My running times are very similar to what I was doing in 2019-2020, when I was world champion. [...] It's just that **the level has gone up** [...]. I ran at **20km/h in Yokohama (2024)**. This is a pace that **5-6 years ago was enough to win some World Series**."

The above plots seem **consistent** with this statement. :chart_with_upwards_trend:
- The figures for women's and men's olympic-format show recent **improvements of the 10k run pace** (green bars) on **WTCS races**. For 2019 -> 2021 -> 2023, paces were:
  - `3:33 -> 3:28 -> 3:23` for women.
  - `3:06 -> 3:04 -> 2:59` for men.
- The `3:00 /km` pace mention by Luis was, in **2023**, **hardly enough to finish between `5`-th and `9`-th on WTCS men's races**.
- The same **`3:00 /km` was, in **2019**, probably enough to win a WTCS**, since the `5`-th to `9`-th places were about `3:06 /km` at that time.

---

In [this other 2024 video](https://youtu.be/5dyR4zNMsmA?t=840):
- **Alex Yee** ( :gb: ) mentions that the **run of 2012 London ( :gb: ) Olympics** is a reference: _"The run was held as the **best run that has ever been done in triathlon**"_.
- He explains: _"In the last season _(2023)_, we had a few races which came very close to that."_
- This statement seems also to be correct: on the run subplot of the men's olympic format figure, **`London 2012` was the fastest until 2023**.
- This [article from triathlon.org](https://www.triathlon.org/news/article/a_chance_for_history_breaking_down_the_stats_of_past_olympic_games), released **just before Paris ( :fr: ) 2024**, confirms: _"Brownlee’s times (London ( :gb: ) 2012) will likely come under threat. Indeed, it seems highly likely that we could see the **first ever sub-29** and **sub-33** minute 10km times in an Olympic triathlon this summer."_
  - The 5-9th men **ran** at the 2024 Paris Olympics **much slower** that the year before for the **test event**.
  - Also, Alex Yee ( :gb: ) won in 2024 with a **29:49** run, compared to **29:00 in 2023**.
  - Because of the **heat** (the men's race started at **10:45 am** instead of 8:00 am)?
  - Or the fatigue caused by the very long swim?
  - Or was the **run course longer** in 2024? In this case the **women's run time improvement** would be even more **impressive**: Beth Potter ( :gb: ) did 32:57 in 2023, compared to **32:42** for Cassandre Beaugrand ( :fr: ) in 2024, who run faster than 30% of men finishers (15 / 50)!

---

**Yokohama** :jp:
- The event took place **13 times** between 2009 and 2024 in an **olympic** format.
  - I do not know if the courses have changed.
  - But if not, the **comparison** should be **very relevant**.
- **Run times have decreased in the last five editions.** :athletic_shoe: 
  - Leading to the best ever times in [2024](https://triathlon.org/results/result/2023_world_triathlon_championship_series_yokohama1/627954).
- It is interesting to note that runs were particularly **good on olympics years** ([2012](https://triathlon.org/results/result/2012_itu_world_triathlon_yokohama/7817), [2016](https://triathlon.org/results/result/2016_itu_world_triathlon_yokohama/280982), [2021](https://triathlon.org/results/result/2021_world_triathlon_yokohama/452691), [2024](https://triathlon.org/results/result/2023_world_triathlon_championship_series_yokohama1/627955)), especially for **women**.
  - Can it be that this race (usually happening early in the season) was used as **qualification criteria** or as a rehearsal, and therefore attracting very fit and motivated athletes?

---

**Hamburg** :de:
- The event took place **12 times** between 2009 and 2024 in a **sprint** format.
- **Run times** have been constant until [**2024**](https://www.triathlon.org/results/result/2024_world_triathlon_championship_series_hamburg/627964), where a **clear improvement** can be seen.
  - The 2024 race was used by many athletes as a **final repetition** before the Olympics. But still, the **improvement is huge**.
  - Can it be that the 2024 run course was shorter? Indeed, the [2024 result page](https://www.triathlon.org/results/result/2024_world_triathlon_championship_series_hamburg/627964) indicates `Run 4.905km (2 laps)` for 2024, compared to `Run 5km (2 laps)` for [2022](https://www.triathlon.org/results/result/2022_world_triathlon_championship_series_hamburg/546857).

---

Impact of **carbon plate running shoes**? :athletic_shoe:
- The Nike Vaporfly [came out in **2017**](https://en.wikipedia.org/wiki/Nike_Vaporfly_and_Tokyo_2020_Olympics_controversy#:~:text=The%20Nike%20Vaporfly%20first%20came,new%20series%20of%20running%20shoes).
- As for Yokohama ( :jp: ), the running paces have been **constantly improving on WTCS since 2017-2018**.
  - Running times were **already good before 2014**.
  - But **since 2021, paces have never been so low.**
- **Carbon plate technology could be one of the main factors** explaining this improvement.
  - But how to explain that running performances on **world-cups** have not followed the same trend?

---

The **bike(s)** :bike:
- On olympic format, bike times have been **drastically improving** (ignoring covid 2020 year) over the past 6 years, especially for the men.
- Can it be due to **tech innovations?**
- Maybe the level has gone up: **it is no longer just about being a good swimmer and an excellent runner?**
- Maybe some athletes tend to **take more risks** on the bike, sometimes reckless as reports Vincent Luis ( :fr: ) in [this interview](https://youtu.be/iCpi2sUh6Ko?si=PFnh-Cgg24PQTSJZ&t=1250).

---

**World-cup vs WTCS** :trophy:
- Apart for 2018, the **running level** is consistently **higher in WTCS than in world-cups**.
- Which could be expected since **WTCS are so much selective**.

---

The swim of [2024 Paris ( :fr: ) Olympics](https://triathlon.org/results/result/paris_2024_olympic_games/655047) was very though because of the **current** on the way back:
- 20:26 (**01:22** /100m) for men.
- 22:33 (**01:30** /100m) for women.

**Care** is needed when comparing **swim times**:
- In the WTCS (green bars), **women's times appear to have reached historic lows**, while 2024 men's times are the third **slowest** since 2009.
- This is likely because, in the two 2024 olympic WTCS events considered (Yokohama ( :jp: ) and Cagliari  ( :it: )), **women swam with wetsuits while men did not**.

---

**Criticisms** :warning:
- Not all events have **identical distances** and conditions.
  - However, **averaging many events** _(the number below the year on the x-axis)_, with multiple venues **repeating every year**, helps to **mitigate this variability**.
- Swim :swimmer:
  - Distances can vary based on **buoy positions**.
  - Differences in **water conditions** (e.g. rough sea, current) can also significantly affect swim times, making comparisons challenging.
  - Last but not least, the **wetsuit** may be allowed or not.  
- Bike :bicyclist:
  - Weather conditions, particularly **wind** and **rain**, can influence bike times.
  - Variations in **course profiles (hilly vs. flat)** can make direct comparisons of bike times unfair.
- Run :running:
  - Run times are generally **more comparable** as World Triathlon run courses tend to be **predominantly flat**, reducing variability.

---

---

# :thermometer: TEMPERATURES

This section examines the recorded **water and air temperatures** and, inspired by the recent work by [Gibson (2024)](https://eprints.qut.edu.au/250162/), investigates their impact on **swimming and running performance**, respectively.

| ![temperatures.png](res/temperatures.png) | 
|:-----------------------------------------:| 
|  *Recorded water and air temperatures.*   |

The **temperature ranges** are **broad**:
- :ocean: 80% of the recorded **water** temperatures are between **16.3 and 26.6 °C**.
  - (**Mean: 21.4 °C**, SD: 3.8 °C, Min: 13.7 °C, Max: 31.8 °C)
- :parasol_on_ground: 80% of the recorded **air** temperatures are between **17.0 and 29.6 °C**.
  - (**Mean: 23.2 °C**, SD: 5.2 °C, Min: 7.6 °C, Max: 35.5 °C)

---

**Several limitations** should be considered:
- **Incomplete data:** Many events lack temperature data, limiting the analysis's comprehensiveness.
- **Pre-race measurements:** Measurements are typically **taken before the event**.
  - Depending on the **race timetable**, the **actual temperature** experienced during the race can be lower or higher than the **reported temperature**.
  - _"Water temperature must be taken **one hour** prior to the start of the event on competition day. It must be taken at the middle of the course and in two other areas on the swim course, at a **depth of 60 cm**."_
  - Air temperatures are likely **recorded before the race** as well, potentially leading to **significant temperature increases** by the time athletes begin the run.
  - For instance, the air temperature for the [men's race (10:45 am)](https://triathlon.org/results/result/paris_2024_olympic_games/655047) at Paris 2024 ( :fr: ) is reported at **23.9 °C**, while it was [closer to **28 °C** during the run](https://www.infoclimat.fr/observations-meteo/archives/31/juillet/2024/paris-montsouris/07156.html). 
- **Humidity Impact:** While humidity could significantly affect running performance, its values are **not reported**.
- Last but not least, **swim and run courses vary in distance**, and water conditions (e.g., waves, salinity, current) also differ between events, making **comparisons challenging**.

:warning: Given these **limitations**, especially the variation in course distances, **conclusions should be drawn with caution**.

---

### :ocean: Water temperatures and swim times

| ![temperatures_water.png](res/temperatures_water.png) | 
|:-----------------------------------------------------:| 
|          *Water temperature and swim times.*          |

The [women's race](https://triathlon.org/results/result/2021_world_triathlon_cup_haeundae/454064) at [Haeundae ( :kr: ) (2021)](https://www.triathlon.org/events/event/2021_world_triathlon_cup_haeundae) is excluded due to an **inconsistency with the 20°C wetsuit rule**:
- The race report notes: _"Water temperature 21.3ºC. Air temperature 15.4º C. Wetsuits allowed."_
- The [2024 rule book](https://www.triathlon.org/uploads/docs/World-Triathlon_Competition-Rules_2024_20240416.pdf) states in section 4.4.b. that _"when the water temperature is at or below 22ºC and the **air temperature** is at or below **15ºC**, then **the value of the water temperature will be adjusted**."_
  - For instance: Air at 15°C and water at 22°C -> The **water temperature is adjusted** at 18.5°C -> Wetsuit allowed.
  - It is possible that the 15°C threshold was higher in 2021, leading to the discrepancy.

Swim appears **slightly faster in water temperatures below 20°C**.
- Likely because **wetsuits are allowed** at these lower temperatures.
- Further research could analyse the **impact of temperature on swim performance** (see already [Gay et al, 2021](https://www.thieme-connect.com/products/ejournals/abstract/10.1055/a-1481-8473)), and try to determine the **optimal water temperature range** for races, with and without wetsuits.

---

<details>
  <summary>Click to expand - ❌ <strong>Anomalies ignored for this analysis.</strong></summary>

|           SWIM CONDITIONS           |                                                                       EVENT                                                                       | WETSUIT | WATER TEMPERATURE (°C) :ocean: | AIR TEMPERATURE (°C) :thermometer: |
|:-----------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------:|:-------:|:------------------------------:|:----------------------------------:|
|    :fire: wetsuit & water>=20°C     |                      [2021 Haeundae (w)](https://www.triathlon.org/events/event/2021_world_triathlon_cup_haeundae) ( :kr: )                       |  True   |              21.3              |        15.4 ( :snowflake: )        |
| :snowflake: no-wetsuit & water<20°C |                       [2014 Chicago (w)](https://www.triathlon.org/events/event/2014_itu_world_triathlon_chicago) ( :us: )                        |  False  |              19.2              |        33.5 ( :hot_face: )         |
| :snowflake: no-wetsuit & water<20°C |                       [2014 Chicago (m)](https://www.triathlon.org/events/event/2014_itu_world_triathlon_chicago) ( :us: )                        |  False  |              19.2              |        33.5 ( :hot_face: )         |
| :snowflake: no-wetsuit & water<20°C |                       [2013 Hamburg (w)](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                        |  False  |              17.4              |                23.8                |
| :snowflake: no-wetsuit & water<20°C |                       [2013 Hamburg (m)](https://www.triathlon.org/events/event/2013_itu_world_triathlon_hamburg) ( :de: )                        |  False  |              18.3              |        29.6 ( :hot_face: )         |
| :snowflake: no-wetsuit & water<20°C |                     [2012 Sydney (m)](https://www.triathlon.org/events/event/2012_itu_world_triathlon_sydney) ( :australia: )                     |  False  |              19.5              |                22.0                |
| :snowflake: no-wetsuit & water<20°C |      [2011 London (w)](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )       |  False  |               17               |                21.8                |
| :snowflake: no-wetsuit & water<20°C |      [2011 London (m)](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_london) ( :gb: )       |  False  |              19.5              |                21.3                |
|    :fire: wetsuit & water>=20°C     | [2011 Kitzbuhel (m)](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_kitzbuhel) ( :austria: ) |  True   |              20.5              |        16.0 ( :snowflake: )        |

As already explained above for [Haeundae ( :kr: ) (2021)](https://www.triathlon.org/events/event/2021_world_triathlon_cup_haeundae), when the **air temperature** is **extreme**, the water temperature is **adjusted**.

But what is the reason for the other **inconsistencies** with the 20°C rule?
- Probably **errors in the data reported**?
- Unless the 20°C threshold was different at the time. 

</details>

---

:swimmer: Some cold and hot **swims**:

|  YEAR  |                                                               EVENT                                                               |  WATER TEMPERATURE  |  DISTANCE  |  EVENT CATEGORY  |
|:------:|:---------------------------------------------------------------------------------------------------------------------------------:|:-------------------:|:----------:|:----------------:|
|  2023  |             [Vina del Mar](https://www.triathlon.org/events/event/2023_world_triathlon_cup_vina_del_mar) ( :chile: )              |  13.7 :cold_face:   |   sprint   |    WORLD-CUP     |
|  2017  |           [Cape Town](https://www.triathlon.org/events/event/2017_cape_town_itu_triathlon_world_cup) ( :south_africa: )           |  13.8 :cold_face:   |   sprint   |    WORLD-CUP     |
|  2022  |             [Vina del Mar](https://www.triathlon.org/events/event/2022_world_triathlon_cup_vina_del_mar) ( :chile: )              |  14.3 :cold_face:   |   sprint   |    WORLD-CUP     |
|  2023  |         [Sunderland](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_sunderland) ( :gb: )         |  14.4 :cold_face:   |   sprint   |       WTCS       |
|  2012  |        [Auckland](https://www.triathlon.org/events/event/2012_itu_world_triathlon_grand_final_auckland) ( :new_zealand: )         |  14.6 :cold_face:   |  olympic   |       WTCS       |
|  2014  |                [Stockholm](https://www.triathlon.org/events/event/2014_itu_world_triathlon_stockholm) ( :sweden: )                |  15.0 :cold_face:   |   sprint   |       WTCS       |
|  2023  |                  [Tongyeong](https://www.triathlon.org/events/event/2023_world_triathlon_cup_tongyeong) ( :kr: )                  |  15.0 :cold_face:   |   sprint   |    WORLD-CUP     |
|  2013  |                [Stockholm](https://www.triathlon.org/events/event/2013_itu_world_triathlon_stockholm) ( :sweden: )                |  15.0 :cold_face:   |  olympic   |       WTCS       |
|  2022  |                   [Bergen](https://www.triathlon.org/events/event/2022_world_triathlon_cup_bergen) ( :norway: )                   |  15.0 :cold_face:   |   sprint   |    WORLD-CUP     |
|  2018  |           [Cape Town](https://www.triathlon.org/events/event/2018_cape_town_itu_triathlon_world_cup) ( :south_africa: )           |  15.0 :cold_face:   |   sprint   |    WORLD-CUP     |
|  ...   |                                                                ...                                                                |         ...         |    ...     |       ...        |
|  2023  |                   [Valencia](https://www.triathlon.org/events/event/2023_world_triathlon_cup_valencia) ( :es: )                   |   29.0 :hot_face:   |  olympic   |    WORLD-CUP     |
|  2017  |    [Mérida, Yucatán, Puerto Progreso](https://www.triathlon.org/events/event/2017_merida_itu_triathlon_world_cup) ( :mexico: )    |   29.0 :hot_face:   |   sprint   |    WORLD-CUP     |
|  2018  |           [Mooloolaba](https://www.triathlon.org/events/event/2018_mooloolaba_itu_triathlon_world_cup) ( :australia: )            |   29.1 :hot_face:   |   sprint   |    WORLD-CUP     |
|  2019  |               [Huatulco](https://www.triathlon.org/events/event/2019_huatulco_itu_triathlon_world_cup) ( :mexico: )               |   29.5 :hot_face:   |   sprint   |    WORLD-CUP     |
|  2018  |               [Huatulco](https://www.triathlon.org/events/event/2018_huatulco_itu_triathlon_world_cup) ( :mexico: )               |   30.0 :hot_face:   |   sprint   |    WORLD-CUP     |
|  2024  |                 [Huatulco](https://www.triathlon.org/events/event/2024_world_triathlon_cup_huatulco) ( :mexico: )                 |   30.0 :hot_face:   |   sprint   |    WORLD-CUP     |
|  2021  |                 [Huatulco](https://www.triathlon.org/events/event/2021_huatulco_triathlon_world_cup) ( :mexico: )                 |   30.0 :hot_face:   |   sprint   |    WORLD-CUP     |
|  2021  | [Abu Dhabi](https://www.triathlon.org/events/event/2021_world_triathlon_championship_series_abu_dhabi) ( :united_arab_emirates: ) |   31.0 :hot_face:   |   sprint   |       WTCS       |
|  2022  |                 [Huatulco](https://www.triathlon.org/events/event/2022_world_triathlon_cup_huatulco) ( :mexico: )                 |   31.0 :hot_face:   |   sprint   |    WORLD-CUP     |
|  2023  |                 [Huatulco](https://www.triathlon.org/events/event/2023_world_triathlon_cup_huatulco) ( :mexico: )                 |   31.8 :hot_face:   |   sprint   |    WORLD-CUP     |

---

### :parasol_on_ground: Air temperatures and run times


| ![temperatures_air.png](res/temperatures_air.png) | 
|:-------------------------------------------------:| 
|         *Air temperature and run times.*          |

A **2nd degree fit** is applied on the scatter plot using [`seaborn.regplot`](https://seaborn.pydata.org/generated/seaborn.regplot.html).
- It suggests a trend where **higher temperatures** correlate with **slower running paces**.
- While no definitive "optimal" temperature can be reliably determined, this trend **aligns** with both [research findings](https://www.outsideonline.com/health/running/racing/race-strategy/how-much-does-heat-slow-your-race-pace/) and **personal experiences** ( :hot_face: ).
- It also underscores the **importance of hydration and cooling strategies**, such as the use of **[cooling headbands](https://conecta.tec.mx/en/news/national/entrepreneurs/goodbye-heat-mexican-creates-band-cool-down-olympic-athletes)**.

:runner: Some cold and hot **runs**:

|  YEAR  |                                                                  EVENT                                                                   |  AIR TEMPERATURE  |  DISTANCE  |  EVENT CATEGORY  |
|:------:|:----------------------------------------------------------------------------------------------------------------------------------------:|:-----------------:|:----------:|:----------------:|
|  2015  |                    [Edmonton](https://www.triathlon.org/events/event/2015_itu_world_triathlon_edmonton) ( :canada: )                     |  7.6 :cold_face:  |   sprint   |       WTCS       |
|  2023  |                     [Tongyeong](https://www.triathlon.org/events/event/2023_world_triathlon_cup_tongyeong) ( :kr: )                      | 10.0 :cold_face:  |   sprint   |    WORLD-CUP     |
|  2023  |                 [Vina del Mar](https://www.triathlon.org/events/event/2023_world_triathlon_cup_vina_del_mar) ( :chile: )                 | 11.0 :cold_face:  |   sprint   |    WORLD-CUP     |
|  2022  |                 [Vina del Mar](https://www.triathlon.org/events/event/2022_world_triathlon_cup_vina_del_mar) ( :chile: )                 | 11.0 :cold_face:  |   sprint   |    WORLD-CUP     |
|  2016  |                    [Edmonton](https://www.triathlon.org/events/event/2016_itu_world_triathlon_edmonton) ( :canada: )                     | 12.7 :cold_face:  |   sprint   |       WTCS       |
|  2021  |                     [Tongyeong](https://www.triathlon.org/events/event/2021_world_triathlon_cup_tongyeong) ( :kr: )                      | 13.2 :cold_face:  |   sprint   |    WORLD-CUP     |
|  2011  | [Kitzbuhel](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_kitzbuhel) ( :austria: ) | 13.5 :cold_face:  |  olympic   |       WTCS       |
|  2018  |            [New Plymouth](https://www.triathlon.org/events/event/2018_new_plymouth_itu_triathlon_world_cup) ( :new_zealand: )            | 13.7 :cold_face:  |   sprint   |    WORLD-CUP     |
|  2023  |                      [Miyazaki](https://www.triathlon.org/events/event/2023_world_triathlon_cup_miyazaki) ( :jp: )                       | 14.3 :cold_face:  |  olympic   |    WORLD-CUP     |
|  2017  |           [Rotterdam](https://www.triathlon.org/events/event/2017_itu_world_triathlon_grand_final_rotterdam) ( :netherlands: )           | 14.4 :cold_face:  |  olympic   |       WTCS       |
|  ...   |                                                                   ...                                                                    |        ...        |    ...     |       ...        |
|  2015  |     [Rio de Janeiro](https://www.triathlon.org/events/event/2015_rio_de_janeiro_itu_world_olympic_qualification_event) ( :brazil: )      |  32.1 :hot_face:  |  olympic   |      GAMES       |
|  2018  |                  [Huatulco](https://www.triathlon.org/events/event/2018_huatulco_itu_triathlon_world_cup) ( :mexico: )                   |  32.1 :hot_face:  |   sprint   |    WORLD-CUP     |
|  2014  |              [Tiszaujvaros](https://www.triathlon.org/events/event/2014_tiszaujvaros_itu_triathlon_world_cup) ( :hungary: )              |  32.4 :hot_face:  |   sprint   |    WORLD-CUP     |
|  2014  |                       [Chicago](https://www.triathlon.org/events/event/2014_itu_world_triathlon_chicago) ( :us: )                        |  33.5 :hot_face:  |  olympic   |       WTCS       |
|  2024  |                    [Huatulco](https://www.triathlon.org/events/event/2024_world_triathlon_cup_huatulco) ( :mexico: )                     |  33.9 :hot_face:  |   sprint   |    WORLD-CUP     |
|  2016  |               [Cozumel](https://www.triathlon.org/events/event/2016_itu_world_triathlon_grand_final_cozumel) ( :mexico: )                |  34.0 :hot_face:  |  olympic   |       WTCS       |
|  2010  |      [Madrid](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_madrid) ( :es: )       |  34.0 :hot_face:  |  olympic   |       WTCS       |
|  2021  |    [Abu Dhabi](https://www.triathlon.org/events/event/2021_world_triathlon_championship_series_abu_dhabi) ( :united_arab_emirates: )     |  34.0 :hot_face:  |   sprint   |       WTCS       |
|  2023  |                    [Huatulco](https://www.triathlon.org/events/event/2023_world_triathlon_cup_huatulco) ( :mexico: )                     |  35.0 :hot_face:  |   sprint   |    WORLD-CUP     |
|  2015  |              [Tiszaujvaros](https://www.triathlon.org/events/event/2015_tiszaujvaros_itu_triathlon_world_cup) ( :hungary: )              |  35.5 :hot_face:  |   sprint   |    WORLD-CUP     |

---

---

# :earth_africa: HOST COUNTRIES

Countries having **hosted more than one** `world-series`, `world-cup` or `games-related` event since 2009:

|            COUNTRY             | COUNT |                                            VENUES                                             |
|:------------------------------:|:-----:|:---------------------------------------------------------------------------------------------:|
|          JPN ( :jp: )          |  21   |                     Yokohama (13), Miyazaki (6), Ishigaki (1), Tokyo (1)                      |
|      AUS ( :australia: )       |  18   |                  Mooloolaba (9), Gold Coast (5), Sydney (3), Wollongong (1)                   |
|          ESP ( :es: )          |  17   | Madrid (7), Valencia (3), Banyoles (2), Pontevedra (2), Palamos (1), Alicante (1), Huelva (1) |
|        MEX ( :mexico: )        |  16   |               Huatulco (8), Cozumel (4), Monterrey (2), Cancun (1), Mérida (1)                |
|          KOR ( :kr: )          |  14   |              Tongyeong (9), Tongyeong  (2), Seoul (1), Haeundae (1), Yeongdo (1)              |
|          GER ( :de: )          |  14   |                                         Hamburg (14)                                          |
|          GBR ( :gb: )          |  14   |                     London (7), Leeds (5), Birmingham (1), Sunderland (1)                     |
|        CAN ( :canada: )        |  13   |                                  Edmonton (9), Montreal (4)                                   |
|     NZL ( :new_zealand: )      |  11   |                          New Plymouth (6), Auckland (4), Napier (1)                           |
|          ITA ( :it: )          |  11   |                             Cagliari (7), Arzachena (3), Rome (1)                             |
|       HUN ( :hungary: )        |  10   |                                       Tiszaujvaros (9)                                        |
|          CHN ( :cn: )          |  10   |                Chengdu (5), Weihai (2), Beijing (1), Jiayuguan (1), Weihai (1)                |
| UAE ( :united_arab_emirates: ) |   8   |                                         Abu Dhabi (8)                                         |
|    CZE ( :czech_republic: )    |   6   |                                       Karlovy Vary (6)                                        |
|          USA ( :us: )          |   6   |                          Des Moines (2), San Diego (2), Chicago (2)                           |
|        SWE ( :sweden: )        |   5   |                                         Stockholm (5)                                         |
|       AUT ( :austria: )        |   4   |                                         Kitzbuhel (4)                                         |
|     RSA ( :south_africa: )     |   4   |                                         Cape Town (4)                                         |
|       BER ( :bermuda: )        |   3   |                                          Bermuda (3)                                          |
|        BRA ( :brazil: )        |   3   |                                      Rio de Janeiro (2)                                       |
|       ECU ( :ecuador: )        |   3   |                                          Salinas (3)                                          |
|     SUI ( :switzerland: )      |   3   |                                         Lausanne (3)                                          |
|        CHI ( :chile: )         |   2   |                                       Vina del Mar (2)                                        |
|          TUR ( :tr: )          |   2   |                                          Alanya (2)                                           |

It can be that some events are missing: these entries come from the data used for this report, after filtering and cleaning.

<details>
  <summary>Click to expand - <strong>Top host countries for world-series.</strong></summary>

|            COUNTRY             | COUNT |                VENUES                 |
|:------------------------------:|:-----:|:-------------------------------------:|
|          GER ( :de: )          |  14   |             Hamburg (14)              |
|          JPN ( :jp: )          |  13   |             Yokohama (13)             |
|          GBR ( :gb: )          |  12   | London (6), Leeds (5), Sunderland (1) |
|        CAN ( :canada: )        |  10   |      Edmonton (7), Montreal (3)       |
|      AUS ( :australia: )       |   8   |      Gold Coast (5), Sydney (3)       |
| UAE ( :united_arab_emirates: ) |   8   |             Abu Dhabi (8)             |
|          ESP ( :es: )          |   6   |      Madrid (5), Pontevedra (1)       |
|        SWE ( :sweden: )        |   5   |             Stockholm (5)             |
|          USA ( :us: )          |   4   |      San Diego (2), Chicago (2)       |
|       AUT ( :austria: )        |   4   |             Kitzbuhel (4)             |

</details>

<details>
  <summary>Click to expand - <strong>Top host countries for world-cups.</strong></summary>

|         COUNTRY          | COUNT |                                            VENUES                                             |
|:------------------------:|:-----:|:---------------------------------------------------------------------------------------------:|
|     MEX ( :mexico: )     |  15   |               Huatulco (8), Cozumel (3), Monterrey (2), Cancun (1), Mérida (1)                |
|       KOR ( :kr: )       |  12   |                   Tongyeong (8), Tongyeong  (2), Haeundae (1), Yeongdo (1)                    |
|       ESP ( :es: )       |  11   | Valencia (3), Banyoles (2), Madrid (2), Palamos (1), Alicante (1), Huelva (1), Pontevedra (1) |
|   AUS ( :australia: )    |  10   |                                Mooloolaba (9), Wollongong (1)                                 |
|       CHN ( :cn: )       |   9   |             Jintang (3), Weihai (2), Chengdu (2), Gansu (1), Weihai, Shandong (1)             |
|    HUN ( :hungary: )     |   9   |                              Tiszaujvaros (7), Tiszaujvaros  (2)                              |
|       ITA ( :it: )       |   8   |                             Cagliari (4), Arzachena (3), Rome (1)                             |
|  NZL ( :new_zealand: )   |   8   |                          New Plymouth (6), Auckland (1), Napier (1)                           |
|       JPN ( :jp: )       |   7   |                                  Miyazaki (6), Ishigaki (1)                                   |
| CZE ( :czech_republic: ) |   6   |                                       Karlovy Vary (6)                                        |

</details>

---

---

# :calendar: SEASON DURATION

This section **examines the duration of the competition season** and the **number of races** athletes participate in.

|                                           ![season_duration.png](res/season_duration.png)                                            | 
|:------------------------------------------------------------------------------------------------------------------------------------:| 
| *Duration of World Cup and World Series seasons, as well as the duration of the seasons of the top 50 athletes in the WTCS ranking.* |


### World-Series

2020, 2021 and to some extent 2022 have been affected by the covid pandemic. Their rows are written in _italic_.

|  Year  |  Num. events  |               Season duration               |    Start    |     End     |                                                             First event                                                              |                                                                    Last event                                                                    |
|:------:|:-------------:|:-------------------------------------------:|:-----------:|:-----------:|:------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------:|
|  2009  |       7       |             127 days (~ 4.2 m)              |  **05**-02  |  **09**-09  | [Tongyeong ( :kr: )](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_series_tongyeong)  | [Gold Coast ( :australia: )](https://www.triathlon.org/events/event/2009_dextro_energy_triathlon_-_itu_world_championship_grand_final_gold_coas) |
|  2010  |       7       |             147 days (~ 4.9 m)              |  **04**-11  |  **09**-08  | [Sydney ( :australia: )](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_world_championship_series_sydney) |   [Budapest ( :hungary: )](https://www.triathlon.org/events/event/2010_dextro_energy_triathlon_-_itu_triathlon_world_championship_grand_final)   |
|  2011  |       8       |             160 days (~ 5.3 m)              |  **04**-09  |  **09**-19  | [Sydney ( :australia: )](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_sydney) |        [Yokohama ( :jp: )](https://www.triathlon.org/events/event/2011_dextro_energy_triathlon_-_itu_world_championship_series_yokohama)         |
|  2012  |       8       |             186 days (~ 6.2 m)              |  **04**-14  |  **10**-20  |                   [Sydney ( :australia: )](https://www.triathlon.org/events/event/2012_itu_world_triathlon_sydney)                   |                [Auckland ( :new_zealand: )](https://www.triathlon.org/events/event/2012_itu_world_triathlon_grand_final_auckland)                |
|  2013  |       7       |             155 days (~ 5.2 m)              |  **04**-06  |  **09**-11  |                [Auckland ( :new_zealand: )](https://www.triathlon.org/events/event/2013_itu_world_triathlon_auckland)                |                      [London ( :gb: )](https://www.triathlon.org/events/event/2013_itu_world_triathlon_grand_final_london)                       |
|  2014  |       7       |             143 days (~ 4.8 m)              |  **04**-06  |  **08**-29  |                [Auckland ( :new_zealand: )](https://www.triathlon.org/events/event/2014_itu_world_triathlon_auckland)                |                  [Edmonton ( :canada: )](https://www.triathlon.org/events/event/2014_itu_world_triathlon_grand_final_edmonton)                   |
|  2015  |       9       |             189 days (~ 6.3 m)              |  **03**-06  |  **09**-15  |          [Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2015_itu_world_triathlon_abu_dhabi)           |                     [Chicago ( :us: )](https://www.triathlon.org/events/event/2015_itu_world_triathlon_grand_final_chicago)                      |
|  2016  |       9       |             186 days (~ 6.2 m)              |  **03**-05  |  **09**-11  |          [Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2016_itu_world_triathlon_abu_dhabi)           |                   [Cozumel ( :mexico: )](https://www.triathlon.org/events/event/2016_itu_world_triathlon_grand_final_cozumel)                    |
|  2017  |       9       |             191 days (~ 6.4 m)              |  **03**-03  |  **09**-14  |          [Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2017_itu_world_triathlon_abu_dhabi)           |               [Rotterdam ( :netherlands: )](https://www.triathlon.org/events/event/2017_itu_world_triathlon_grand_final_rotterdam)               |
|  2018  |       8       |             190 days (~ 6.3 m)              |  **03**-02  |  **09**-12  |          [Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2018_itu_world_triathlon_abu_dhabi)           |               [Gold Coast ( :australia: )](https://www.triathlon.org/events/event/2018_itu_world_triathlon_grand_final_gold_coast)               |
|  2019  |       8       |             171 days (~ 5.7 m)              |  **03**-08  |  **08**-29  |          [Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2019_itu_world_triathlon_abu_dhabi)           |                [Lausanne ( :switzerland: )](https://www.triathlon.org/events/event/2019_itu_world_triathlon_grand_final_lausanne)                |
| _2020_ |      _1_      | _0 days_ ( :mask: :face_with_thermometer: ) | _**09**-05_ | _**09**-05_ |                    _[Hamburg ( :de: )](https://www.triathlon.org/events/event/2020_itu_world_triathlon_hamburg)_                     |                          _[Hamburg ( :de: )](https://www.triathlon.org/events/event/2020_itu_world_triathlon_hamburg)_                           |
| _2021_ |      _5_      |            _170 days (~ 5.7 m)_             | _**05**-15_ | _**11**-05_ |                     _[Yokohama ( :jp: )](https://www.triathlon.org/events/event/2021_world_triathlon_yokohama)_                      |       _[Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2021_world_triathlon_championship_series_abu_dhabi)_        |
| _2022_ |      _6_      |            _190 days (~ 6.3 m)_             | _**05**-14_ | _**11**-24_ |           _[Yokohama ( :jp: )](https://www.triathlon.org/events/event/2022_world_triathlon_championship_series_yokohama)_            |       _[Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2022_world_triathlon_championship_finals_abu_dhabi)_        |
|  2023  |       6       |             199 days (~ 6.6 m)              |  **03**-03  |  **09**-22  |  [Abu Dhabi ( :united_arab_emirates: )](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_abu_dhabi)   |                [Pontevedra ( :es: )](https://www.triathlon.org/events/event/2023_world_triathlon_championship_finals_pontevedra)                 |
|  2024  |       2       |              14 days (~ 0.5 m)              |  **05**-11  |  **05**-25  |            [Yokohama ( :jp: )](https://www.triathlon.org/events/event/2023_world_triathlon_championship_series_yokohama1)            |                  [Cagliari ( :it: )](https://www.triathlon.org/events/event/2024_world_triathlon_championship_series_cagliari)                   |


### World-Cups


|  Year  |  Num. events  |   Season duration    |    Start    |     End     |                                                  First event                                                   |                                                 Last event                                                 |
|:------:|:-------------:|:--------------------:|:-----------:|:-----------:|:--------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------:|
|  2009  |       3       |  131 days (~ 4.4 m)  |  **06**-27  |  **11**-08  |       [Des Moines ( :us: )](https://www.triathlon.org/events/event/2009_hy-vee_itu_triathlon_elite_cup)        |   [Huatulco ( :mexico: )](https://www.triathlon.org/events/event/2009_huatulco_itu_triathlon_world_cup)    |
|  2010  |       5       |  193 days (~ 6.4 m)  |  **03**-27  |  **10**-10  |  [Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2010_mooloolaba_itu_triathlon_world_cup)  |   [Huatulco ( :mexico: )](https://www.triathlon.org/events/event/2010_huatulco_itu_triathlon_world_cup)    |
|  2011  |       8       |  234 days (~ 7.8 m)  |  **03**-26  |  **11**-20  |  [Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2011_mooloolaba_itu_triathlon_world_cup)  | [Auckland ( :new_zealand: )](https://www.triathlon.org/events/event/2011_auckland_itu_triathlon_world_cup) |
|  2012  |       7       |  193 days (~ 6.4 m)  |  **03**-24  |  **10**-07  |  [Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2012_mooloolaba_itu_triathlon_world_cup)  |     [Cancun ( :mexico: )](https://www.triathlon.org/events/event/2012_cancun_itu_triathlon_world_cup)      |
|  2013  |      10       |  221 days (~ 7.4 m)  |  **03**-16  |  **10**-27  |  [Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2013_mooloolaba_itu_triathlon_world_cup)  |   [Guatape ( :colombia: )](https://www.triathlon.org/events/event/2013_guatape_itu_triathlon_world_cup)    |
|  2014  |       9       |  213 days (~ 7.1 m)  |  **03**-15  |  **10**-18  |  [Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2014_mooloolaba_itu_triathlon_world_cup)  |    [Tongyeong ( :kr: )](https://www.triathlon.org/events/event/2014_tongyeong_itu_triathlon_world_cup)     |
|  2015  |       7       |  220 days (~ 7.3 m)  |  **03**-14  |  **10**-24  |  [Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2015_mooloolaba_itu_triathlon_world_cup)  |    [Tongyeong ( :kr: )](https://www.triathlon.org/events/event/2015_tongyeong_itu_triathlon_world_cup)     |
|  2016  |      10       |  227 days (~ 7.6 m)  |  **03**-12  |  **10**-29  |  [Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2016_mooloolaba_itu_triathlon_world_cup)  |     [Miyazaki ( :jp: )](https://www.triathlon.org/events/event/2016_miyazaki_itu_triathlon_world_cup)      |
|  2017  |      12       |  263 days (~ 8.8 m)  |  **02**-11  |  **11**-04  | [Cape Town ( :south_africa: )](https://www.triathlon.org/events/event/2017_cape_town_itu_triathlon_world_cup)  |     [Miyazaki ( :jp: )](https://www.triathlon.org/events/event/2016_miyazaki_itu_triathlon_world_cup1)     |
|  2018  |      11       |  269 days (~ 9.0 m)  |  **02**-11  |  **11**-10  | [Cape Town ( :south_africa: )](https://www.triathlon.org/events/event/2018_cape_town_itu_triathlon_world_cup)  |     [Miyazaki ( :jp: )](https://www.triathlon.org/events/event/2018_miyazaki_itu_triathlon_world_cup)      |
|  2019  |      13       |  257 days (~ 8.6 m)  |  **02**-09  |  **10**-26  | [Cape Town ( :south_africa: )](https://www.triathlon.org/events/event/2019_cape_town_itu_triathlon_world_cup)  |     [Miyazaki ( :jp: )](https://www.triathlon.org/events/event/2019_miyazaki_itu_triathlon_world_cup)      |
| _2020_ |      _4_      | _233 days (~ 7.8 m)_ | _**03**-14_ | _**11**-07_ | _[Mooloolaba ( :australia: )](https://www.triathlon.org/events/event/2020_mooloolaba_itu_triathlon_world_cup)_ |    _[Valencia ( :es: )](https://www.triathlon.org/events/event/2020_valencia_itu_triathlon_world_cup)_     |
| _2021_ |      _6_      | _158 days (~ 5.3 m)_ | _**05**-22_ | _**10**-30_ |       _[Lisbon ( :portugal: )](https://www.triathlon.org/events/event/2021_world_triathlon_cup_lisbon)_        |     _[Tongyeong  ( :kr: )](https://www.triathlon.org/events/event/2021_world_triathlon_cup_tongyeong)_     |
| _2022_ |      _9_      | _165 days (~ 5.5 m)_ | _**05**-28_ | _**11**-13_ |       _[Arzachena ( :it: )](https://www.triathlon.org/events/event/2022_world_triathlon_cup_arzachena)_        | _[Vina del Mar ( :chile: )](https://www.triathlon.org/events/event/2022_world_triathlon_cup_vina_del_mar)_ |
|  2023  |      14       |  226 days (~ 7.5 m)  |  **03**-25  |  **11**-11  | [New Plymouth ( :new_zealand: )](https://www.triathlon.org/events/event/2023_world_triathlon_cup_new_plymouth) |  [Vina del Mar ( :chile: )](https://www.triathlon.org/events/event/2023_world_triathlon_cup_vina_del_mar)  |
|  2024  |       6       |  84 days (~ 2.8 m)   |  **02**-24  |  **05**-18  |       [Napier ( :new_zealand: )](https://www.triathlon.org/events/event/2024_world_triathlon_cup_napier)       |  [Samarkand ( :uzbekistan: )](https://www.triathlon.org/events/event/2024_world_triathlon_cup_samarkand)   |


## Athlete seasons

The following plots represent the **seasons** (columns) of **50 athletes** (rows).
- The top-50 of **[`World Triathlon Championship Series Rankings`](https://triathlon.org/rankings/world_triathlon_championship_series/male)** is used.
- The [`World Triathlon Rankings`](https://triathlon.org/rankings/world_triathlon_rankings/male) would have been preferred since it takes both **world-cups** and **world-series** into consideration.
  - Unfortunately, I could not find any archive for 2018, 2020, 2021, 2023. :disappointed:

| ![athlete_season_duration_m.png](res/athlete_season_duration_m.png) | 
|:-------------------------------------------------------------------:| 
|               *Seasons of the top-50 athletes. Men.*                |

| ![athlete_season_duration_w.png](res/athlete_season_duration_w.png) | 
|:-------------------------------------------------------------------:| 
|              *Seasons of the top-50 athletes. Women.*               |

**Top athletes** seem to **prefer world series over world cups** (more red than blue in the top rows).
- Probably because WTCS events offer **more points** and **prize money**.
- Some athletes do not race in any world cup events (light blue background).

Regarding the **competition season**: from 2009 to 2019, it **became longer**.
- The 2009 WTCS season started in May, but from 2015-2019, it began in early March.
- In 2023, the WTCS season was **6.5 months long**, compared to **4.2 months in 2009**.
- The number of world cup events increased significantly during this period: from **3 in 2009 to 13 in 2019**.
  - The **2018 world cup** season lasted **9 months**.
- The **COVID-19 pandemic halted this trend**, although 2023 seems similar to 2019.
  - The ranking process became complicated: e.g., some 2021 races were considered for the 2022 ranking.

Regarding the **athletes' season**: it **follows** the competition season.
- Their World Triathlon season extended **from 130 days in 2009** to **200 days in 2023**.
- On average, athletes raced **10 times in 2019** and **2023**, compared to **6 times in 2009**.

The results found (**number of races** and **season duration**) are **lower bounds**:
- Athletes participate in **other formats besides World Triathlon olympic and sprint** races.
  - For instance, the [French Grand Prix](https://en.wikipedia.org/wiki/Grand_Prix_de_Triathlon) was very popular in the 2010s.
  - Some athletes are racing the [supertri](https://supertri.com/) and **Ironman 70.3** formats as well.
- Their competition season is probably longer, including **indoor races** in the **winter**.

---

---

# :earth_africa: ATHLETE NATIONS

This table examines the **nationalities** of **athletes in the top-50s** of the [`WTCS Ranking`](https://triathlon.org/rankings/world_triathlon_championship_series/male) from 2009 to 2023:

|  RANGE (%)  |                                                                                  NATIONS (W)                                                                                  |                                                                                                                                                       NATIONS (M)                                                                                                                                                       |
|:-----------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|    11-12    |                                                                                 :us:  (11.0%)                                                                                 |                                                                                                                                                                                                                                                                                                                         |
|    10-11    |                                                                      :gb:  (10.9%)  :australia:  (10.1%)                                                                      |                                                                                                                                                                                                                                                                                                                         |
|    9-10     |                                                                                                                                                                               |                                                                                                                                                      :fr:  (9.6%)                                                                                                                                                       |
|     8-9     |                                                                                 :jp:  (8.0%)                                                                                  |                                                                                                                                               :gb:  (8.4%)  :de:  (8.1%)                                                                                                                                                |
|     7-8     |                                                                                 :de:  (7.6%)                                                                                  |                                                                                                                                            :australia:  (7.7%)  :es:  (7.0%)                                                                                                                                            |
|     6-7     |                                                                                                                                                                               |                                                                                                                                                      :us:  (6.1%)                                                                                                                                                       |
|     5-6     |                                                                      :new_zealand:  (5.7%)  :fr:  (5.0%)                                                                      |                                                                                                                                                                                                                                                                                                                         |
|     4-5     |                                                                                                                                                                               |                                                                                                                   :new_zealand:  (4.6%)  :switzerland:  (4.6%)  :canada:  (4.4%)  :portugal:  (4.3%)                                                                                                                    |
|     3-4     |                                          :canada:  (3.7%)  :es:  (3.7%)  :it:  (3.7%)  :netherlands:  (3.6%)  :switzerland:  (3.3%)                                           |                                                                                                                                          :ru:  (3.6%)  :south_africa:  (3.4%)                                                                                                                                           |
|     2-3     |                                                             :austria:  (2.6%)  :mexico:  (2.1%)  :brazil:  (2.0%)                                                             |                                                                                                          :jp:  (2.9%)  :belgium:  (2.9%)  :hungary:  (2.6%)  :it:  (2.4%)  :norway:  (2.4%)  :mexico:  (2.3%)                                                                                                           |
|     1-2     | :belgium:  (1.9%)  :czech_republic:  (1.7%)  :south_africa:  (1.7%)  :ru:  (1.6%)  :poland:  (1.3%)  :hungary:  (1.3%)  :bermuda:  (1.3%)  :chile:  (1.1%)  :ireland:  (1.0%) |                                                                                                   :brazil:  (1.7%)  :white_flag:  (1.4%)  :austria:  (1.1%)  :slovakia:  (1.1%)  :ireland:  (1.0%)  :israel:  (1.0%)                                                                                                    |
|     0-1     |           :portugal:  (0.9%)  :sweden:  (0.7%)  :denmark:  (0.7%)  :luxembourg:  (0.4%)  :ukraine:  (0.4%)  :slovenia:  (0.4%)  :norway:  (0.4%)  :estonia:  (0.1%)           | :kazakhstan:  (0.7%)  :azerbaijan:  (0.7%)  :denmark:  (0.7%)  :czech_republic:  (0.6%)  :ukraine:  (0.3%)  :costa_rica:  (0.3%)  :puerto_rico:  (0.3%)  :barbados:  (0.3%)  :netherlands:  (0.3%)  :argentina:  (0.3%)  :luxembourg:  (0.3%)  :poland:  (0.1%)  :colombia:  (0.1%)  :morocco:  (0.1%)  :chile:  (0.1%) |

### :ticket: Olympics qualification

The **Olympics competition** has **55 spots**, with a limit of **3 athletes per nations**.

Considering nations with a high percentage of athletes in top-50, let's estimate **how many athletes miss the Olympics** because of **the _'max-3-rule'_**:
- **Women:**
  - :us: : ~11.0% => **~3.0** top-50 athletes rejected. :disappointed:
  - :gb: : ~10.9% => **~3.0** top-50 athletes rejected. :disappointed:
  - :australia: : ~10.1% => **~2.6** top-50 athletes rejected. :disappointed:
  - :jp: : ~8.0% => **~1.4** top-50 athletes rejected. :disappointed:
  - :de: : ~7.6% => **~1.2** top-50 athletes rejected. :disappointed:
  - :new_zealand: : ~5.7% => ~0.1 top-50 athlete rejected. :disappointed:
- **Men:**
  - :fr: : ~9.6% => **~2.3** top-50 athletes rejected. :disappointed:
  - :gb: : ~8.4% => **~1.6** top-50 athletes rejected. :disappointed:
  - :de: : ~8.1% => **~1.5** top-50 athletes rejected. :disappointed:
  - :australia: : ~7.7% => **~1.2** top-50 athletes rejected. :disappointed:
  - :es: : ~7.0% => ~0.9 top-50 athlete rejected. :disappointed:
  - :us: : ~6.1% => ~0.4 top-50 athlete rejected. :disappointed:

The estimated **numbers of rejections** are probably **lower bounds**:
- World Triathlon **limits the number of athletes per nation** for its races too.
  - As a result, some strong athletes, such as US women, cannot participate in important World Triathlon races, and thus do not gain points for the ranking.

The percentages are **averages** since 2009. Some years, they can be **much higher**:
- For instance, **8 women in the top-50** (**16.0%**) for:
  - :us: [2015](https://triathlon.org/rankings/itu_world_triathlon_series_2015/female) (a pre-olympics year), with **6 top-30** and the **4th athlete was ranked 16th**.
  - :us: [2016](https://triathlon.org/rankings/itu_world_triathlon_series_2016/female), with **6 top-20**.
  - :australia: [2017](https://triathlon.org/rankings/itu_world_triathlon_series_2017/female).
  - :gb: [2021](https://triathlon.org/rankings/world_triathlon_championship_series_2021/female), with **8 top-30**.
    - The same year, :us: had **5 athletes in the top-12**.

It is no wonder that some athletes **change nationality** to try to qualify for the Olympics.

---

---

# :baby: AGE

|          ![ages.png](res/ages.png)           | 
|:--------------------------------------------:| 
| *Age of athletes ranked 5th-9th over years.* |

Athletes finishing 5th-9th are, on average, **26.3 to 27.7** years old.
- Ages are **similar** for **women and men**.
- Athletes are **slightly older** in the **olympic format** compared to the sprint format: about **1 year difference**.
  - _I would have expected a larger difference._
- There are some small variations, but **no significant trends over the years**.
- Do Olympics punctuate athletes' careers? The age of women on the olympic format reaches local peaks at the years of the Olympic Games in Rio ( :brazil : ), Tokyo ( :jp : ) and Paris ( :fr : ).

---

---

# :checkered_flag: AGE OF LAST RACE

|  ![ages_of_last_race.png](res/ages_of_last_race.png)  | 
|:-----------------------------------------------------:| 
| *Age of last world-cup, world-series or major games.* |

The **average age** of the last race is **similar for women and men**: around **31 years**.

The **distribution is broad** (`~4y std`), because there are **various reasons** for ending a World Triathlon sprint- and olympic-distance top career, such as:
- **Age limit** for elite sport.
- Transitioning to **longer-distance** triathlons
- **Injury**.
- **Personal reasons**, such as pregnancy or changing careers.

Some **extreme values**:
- **`<25` years**:
  - Hollie Avil ( :gb: ): **21y**, 13 races.
  - Kirsten Nuyes ( :netherlands: ): **22y**, 21 races.
  - Ellen Pennock ( :canada: ): **23y**, 17 races.
  - Hanna Philippin ( :de: ): **24y**, 32 races.
  - Marc Austin ( :gb: ): **24y**, 25 races.
  - Sophia Saller ( :de: ): **24y**, 26 races.
  - Oliver Freeman ( :gb: ): **24y**, 20 races.
  - Raphael Montoya ( :fr: ): **24y**, 21 races.
- **`>38` years**:
  - Magali Di Marco Messmer ( :switzerland: ): **39y**, 52 races.
  - Greg Bennett ( :australia: ): **39y**, 70 races.
  - Hunter Kemper ( :us: ): **39y**, 65 races.
  - Kate Allen ( :austria: ): **39y**, 24 races.
  - Samantha Warriner ( :new_zealand: ): **42y**, 48 races.
  - Kiyomi Niwata ( :jp: ): **43y**, 96 races.

<details>
  <summary>Click to expand - 📜 <strong>Full list.</strong></summary>

|         ATHLETE          |     COUNTRY      |  AGE OF LAST RACE  |  NUMBER OF RACES  |
|:------------------------:|:----------------:|:------------------:|:-----------------:|
|       Hollie Avil        |       :gb:       |         21         |        13         |
|      Kirsten Nuyes       |  :netherlands:   |         22         |        21         |
|      Ellen Pennock       |     :canada:     |         23         |        17         |
|     Hanna Philippin      |       :de:       |         24         |        32         |
|       Marc Austin        |       :gb:       |         24         |        25         |
|      Sophia Saller       |       :de:       |         24         |        26         |
|      Oliver Freeman      |       :gb:       |         24         |        20         |
|     Raphael Montoya      |       :fr:       |         24         |        21         |
|    Akane Tsuchihashi     |       :jp:       |         25         |        27         |
|     Sarissa De Vries     |  :netherlands:   |         25         |        26         |
|        Ron Darmon        |     :israel:     |         25         |        44         |
|       Daniela Ryf        |  :switzerland:   |         25         |        42         |
|      Artem Parienko      |       :ru:       |         26         |        23         |
|    Jose Miguel Perez     |       :es:       |         26         |        30         |
|       James Seear        |   :australia:    |         26         |        29         |
|     Gareth Halverson     |   :australia:    |         26         |        17         |
|     Lucy Buckingham      |       :gb:       |         26         |        44         |
|      David McNamee       |       :gb:       |         26         |        34         |
|      Wian Sullwald       |  :south_africa:  |         26         |        70         |
|      Natalie Milne       |       :gb:       |         27         |        14         |
|       Aaron Harris       |       :gb:       |         27         |        27         |
|      Franz Löschke       |       :de:       |         27         |        36         |
|    Andrey Bryukhankov    |       :ru:       |         27         |        36         |
|      Paul Tichelaar      |     :canada:     |         27         |        33         |
|      Felicity Abram      |   :australia:    |         27         |        46         |
|      Mariya Shorets      |       :ru:       |         27         |        47         |
|      Sebastian Rank      |       :de:       |         27         |        28         |
|      Matthew Sharp       |       :gb:       |         27         |        22         |
|       Jenna Parker       |       :us:       |         28         |        21         |
|      Denis Vasiliev      |       :ru:       |         28         |        29         |
|      Benjamin Shaw       |    :ireland:     |         28         |        50         |
|    Sarah-Anne Brault     |     :canada:     |         28         |        32         |
|     Agnieszka Jerzyk     |     :poland:     |         28         |        52         |
|       Andrew Yorke       |     :canada:     |         28         |        42         |
|      Maaike Caelers      |  :netherlands:   |         28         |        56         |
|   Tamara Gomez Garrido   |       :es:       |         28         |        32         |
|       Ivan Tutukin       |   :kazakhstan:   |         28         |        34         |
|     Rebecca Robisch      |       :de:       |         28         |        46         |
|      Kathrin Muller      |       :de:       |         28         |        39         |
|    Kirsten Sweetland     |     :canada:     |         28         |        49         |
|      Paula Findlay       |     :canada:     |         28         |        41         |
|       Peter Croes        |    :belgium:     |         28         |        58         |
|      Kaitlin Donner      |       :us:       |         28         |        37         |
|       Jason Wilson       |    :barbados:    |         28         |        45         |
|      William Clarke      |       :gb:       |         28         |        44         |
|      Jodie Swallow       |       :gb:       |         29         |        32         |
|       Vanessa Raw        |       :gb:       |         29         |        25         |
|     Emmie Charayron      |       :fr:       |         29         |        43         |
|      Katie Hewison       |       :gb:       |         29         |        16         |
|     Jillian Elliott      |       :us:       |         29         |        31         |
|     Andreas Giglmayr     |    :austria:     |         29         |        51         |
|     Radka Kahlefeldt     | :czech_republic: |         29         |        31         |
|    Danne Boterenbrood    |  :netherlands:   |         29         |        20         |
|     Charlotte Bonin      |       :it:       |         29         |        62         |
|      Svenja Bazlen       |       :de:       |         29         |        28         |
|      Elizabeth May       |   :luxembourg:   |         29         |        55         |
|     Annabel Luxford      |   :australia:    |         29         |        52         |
|   Anastasia Abrosimova   |       :ru:       |         29         |        44         |
|       Cameron Good       |   :australia:    |         30         |        33         |
|        Mari Rabie        |  :south_africa:  |         30         |        50         |
|      Brendan Sexton      |   :australia:    |         30         |        57         |
|      Kathy Tremblay      |     :canada:     |         30         |        54         |
|      Jodie Stimpson      |       :gb:       |         30         |        71         |
|      Laurent Vidal       |       :fr:       |         30         |        61         |
|     Yulian Malyshev      |       :ru:       |         30         |        33         |
|     Mark Buckingham      |       :gb:       |         30         |        22         |
|     Gregor Buchholz      |       :de:       |         30         |        59         |
|      Debbie Tanner       |  :new_zealand:   |         30         |        55         |
|     Pamella Oliveira     |     :brazil:     |         30         |        62         |
|        India Lee         |       :gb:       |         31         |        18         |
|  Valentin Mechsheryakov  |   :kazakhstan:   |         31         |        51         |
|      Lauren Groves       |     :canada:     |         31         |        57         |
|    Christian Prochnow    |       :de:       |         31         |        41         |
|       Matt Chrabot       |       :us:       |         31         |        43         |
|      Melanie Hauss       |  :switzerland:   |         31         |        45         |
|       Clark Ellice       |  :new_zealand:   |         31         |        53         |
|       Gavin Noble        |    :ireland:     |         31         |        38         |
|        Tony Dodds        |  :new_zealand:   |         31         |        58         |
|      Emma Snowsill       |   :australia:    |         31         |        44         |
|     Miguel Arraiolos     |    :portugal:    |         31         |        72         |
|       Ricarda Lisk       |       :de:       |         31         |        63         |
|       Line Jensen        |    :denmark:     |         31         |        20         |
|        Ruedi Wild        |  :switzerland:   |         31         |        55         |
|       Kate Roberts       |  :south_africa:  |         31         |        56         |
|    Helle Frederiksen     |    :denmark:     |         31         |        28         |
|        Joe Maloy         |       :us:       |         31         |        37         |
|     Aurelien Raphael     |       :fr:       |         31         |        59         |
|        Dan Wilson        |   :australia:    |         31         |        59         |
|    Annamaria Mazzetti    |       :it:       |         31         |        77         |
|      Rebecca Spence      |  :new_zealand:   |         31         |        39         |
|     Simon De Cuyper      |    :belgium:     |         32         |        55         |
|       David Hauss        |       :fr:       |         32         |        54         |
|       Erin Densham       |   :australia:    |         32         |        64         |
|      Premysl Svarc       | :czech_republic: |         32         |        74         |
|        Yurie Kato        |       :jp:       |         32         |        52         |
|      Helen Jenkins       |       :gb:       |         32         |        55         |
|       Emma Moffatt       |   :australia:    |         32         |        76         |
|       Jan Frodeno        |       :de:       |         32         |        50         |
|     Leonardo Chacon      |   :costa_rica:   |         32         |        86         |
|        Kyle Jones        |     :canada:     |         32         |        90         |
|  Alexander Bryukhankov   |       :ru:       |         32         |        86         |
|      Brent McMahon       |     :canada:     |         32         |        71         |
|      Manuel Huerta       |  :puerto_rico:   |         32         |        60         |
|      Liz Blatchford      |       :gb:       |         32         |        62         |
|       Mark Fretta        |       :us:       |         32         |        70         |
|      Ivan Vasiliev       |       :ru:       |         32         |        81         |
|      Nicky Samuels       |  :new_zealand:   |         33         |        76         |
|     Brad Kahlefeldt      |   :australia:    |         33         |        78         |
|        Bruno Pais        |    :portugal:    |         33         |        64         |
|       Lisa Norden        |     :sweden:     |         33         |        67         |
|       Kate Mcilroy       |  :new_zealand:   |         33         |        39         |
|      Jonathan Zipf       |       :de:       |         33         |        46         |
|      Mariko Adachi       |       :jp:       |         33         |        61         |
|      Tomoko Sonoda       |       :jp:       |         33         |        34         |
|      Irina Abysova       |       :ru:       |         33         |        48         |
|        Anne Haug         |       :de:       |         33         |        45         |
|  Gonzalo Raul Tellechea  |   :argentina:    |         33         |        51         |
|    Frederic Belaubre     |       :fr:       |         33         |        44         |
|     Mary Beth Ellis      |       :us:       |         33         |        24         |
|     Lindsey Jerdonek     |       :us:       |         33         |        38         |
|       Margit Vanek       |    :hungary:     |         33         |        59         |
|      Misato Takagi       |       :jp:       |         33         |        31         |
|       Carole Peon        |       :fr:       |         34         |        55         |
|      Claude Eksteen      |  :south_africa:  |         34         |        25         |
|   Marina Damlaimcourt    |       :es:       |         34         |        53         |
|     Thomas Springer      |    :austria:     |         34         |        41         |
|       Aileen Reid        |    :ireland:     |         34         |        60         |
|      Danylo Sapunov      |    :ukraine:     |         34         |        78         |
|     Jarrod Shoemaker     |       :us:       |         34         |        93         |
|         Tim Don          |       :gb:       |         34         |        73         |
|     Christiane Pilz      |       :de:       |         34         |        40         |
|     Grégory Rouault      |       :us:       |         34         |        19         |
|    Katrien Verstuyft     |    :belgium:     |         34         |        53         |
| Zuriñe Rodriguez Sanchez |       :es:       |         34         |        63         |
|      Sarah Haskins       |       :us:       |         34         |        41         |
|       Maik Petzold       |       :de:       |         34         |        61         |
|   Felicity Sheedy-Ryan   |   :australia:    |         34         |        50         |
|     Hirokatsu Tayama     |       :jp:       |         35         |        87         |
|       Lisa Mensink       |     :canada:     |         35         |        42         |
|       Kris Gemmell       |  :new_zealand:   |         35         |        84         |
|      Sven Riederer       |  :switzerland:   |         35         |        87         |
|      Bevan Docherty      |  :new_zealand:   |         35         |        78         |
|        Andy Potts        |       :us:       |         35         |        32         |
|        Zita Szabó        |    :hungary:     |         35         |        44         |
|       Adam Bowden        |       :gb:       |         35         |        49         |
|     Jessica Harrison     |       :fr:       |         36         |        81         |
|     Cedric Fleureton     |       :fr:       |         36         |        36         |
|       Mateja Šimic       |    :slovenia:    |         36         |        47         |
|       Bryan Keane        |    :ireland:     |         36         |        45         |
|      Marek Jaskolka      |     :poland:     |         36         |        49         |
|        Sarah True        |       :us:       |         36         |        85         |
|        Kerry Lang        |       :gb:       |         36         |        43         |
|  Vladimir Turbayevskiy   |       :ru:       |         36         |        67         |
|       Tony Moulai        |       :fr:       |         37         |        58         |
|      Diogo Sclebin       |     :brazil:     |         37         |        81         |
|      Laura Bennett       |       :us:       |         37         |        68         |
|    Courtney Atkinson     |   :australia:    |         37         |        68         |
|         Reto Hug         |  :switzerland:   |         37         |        67         |
|     Simon Whitfield      |     :canada:     |         37         |        78         |
|     Ryosuke Yamamoto     |       :jp:       |         37         |        82         |
| Ainhoa Murua Zubizarreta |       :es:       |         38         |        100        |
| Magali Di Marco Messmer  |  :switzerland:   |         39         |        52         |
|       Greg Bennett       |   :australia:    |         39         |        70         |
|      Hunter Kemper       |       :us:       |         39         |        65         |
|        Kate Allen        |    :austria:     |         39         |        24         |
|    Samantha Warriner     |  :new_zealand:   |         42         |        48         |
|      Kiyomi Niwata       |       :jp:       |         43         |        96         |

</details>

---

---

# :date: MONTH OF BIRTH

For this section and the next one about [Body mass index](#weight_lifting-BODY-MASS-INDEX), a **larger dataset** is used:
- **All athletes** part of a **non-para ranking**, and aged between 15 and 45 years, are considered.
  - The **ranking categories** defined by World Triathlon can be found [here](https://developers.triathlon.org/reference/rankings-api-overview).
- Leading to a total of **3,439 unique athletes**, including 1,382 women and 2,057 men.

The **month-of-birth** distribution of the athletes is compared to **two reference distributions**:
- Reference #1: **Uniform** month-of-birth distribution.
  - It could be **expected** that each month accounts for **`1/12 = 8.3%`** of the births.
- Reference #2: Birth data collected by the **United Nation**: [data.un.org](https://data.un.org/Data.aspx?d=POP&f=tableCode%3A55).
  - Birth data of people aged between 20 and 30 years are considered, leading to **over 230 million entries**.
  - It could be **expected** that World Triathlon (formerly **ITU**) and **UN** month-of-birth distributions **match**.

|                    ![](res/birth_months.png)                     |
|:----------------------------------------------------------------:|
| *Month-of-birth of World Triathlon (formerly **ITU**) athletes.* |

The results are even more striking when considering the **year quarters**.

|                       ![](res/birth_quarters.png)                       |
|:-----------------------------------------------------------------------:|
| *Year-quarter-of-birth of World Triathlon (formerly **ITU**) athletes.* |

---

<details>
  <summary>Click to expand - 👫 <strong>Same plot with gender comparison.</strong></summary>

|                   ![](res/birth_quarters_gender.png)                    |
|:-----------------------------------------------------------------------:|
| *Year-quarter-of-birth of World Triathlon (formerly **ITU**) athletes.* |

</details>

---

<details>
  <summary>Click to expand - 👶 <strong>Same plot for the Junior categories.</strong></summary>

The average age is 19.5 years.

|                              ![](res/birth_quarters_gender_junior.png)                               |
|:----------------------------------------------------------------------------------------------------:|
| *Year-quarter-of-birth of World Triathlon (formerly **ITU**) athletes in the **Junior** categories.* |

</details>

---

<details>
  <summary>Click to expand - 📊 <strong>Reference distribution from the United Nations.</strong></summary>

|                                                                  ![](res/birth_months_un.png)                                                                   |
|:---------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| *Month-of-birth distribution of the population aged 20-30 recorded by **UN**. Data source: [data.un.org](https://data.un.org/Data.aspx?d=POP&f=tableCode%3A55)* |

</details>

---

> _Can these discrepancies be due to differences between the two datasets (ITU and UN), such as the geographical origin of the births?_

<details>
  <summary>Click to expand - 🌍 <strong>Continent analysis.</strong></summary>

The **continent distributions** differ between the World Triathlon and the UN datasets:

- **ITU dataset:** Europe is predominant (~59%). Asia  (~13%) and North America (~11%) follow.
- **UN dataset:** Asia (~34%), Europe (29%) and North America (24%) form a more uniform top-3.

|                        ![](res/birth_continents.png)                        |
|:---------------------------------------------------------------------------:|
| *Continents distribution of the World Triathlon (formerly **ITU**) dataset* |

|                   ![](res/birth_continents_un.png)                   |
|:--------------------------------------------------------------------:|
| *Continents distribution of the **UN** dataset (used as reference).* |

Note: The UN dataset has probably missed data from African and Asian countries such as China, India and Nigeria.

|                ![](res/birth_continents_un_cumulative.png)                |
|:-------------------------------------------------------------------------:|
| *Another visualization of the **reference month-of-birth distribution**.* |

The month-of-birth and quarter-of-birth distributions for **each continent** can be visualized:

|   ![](res/birth_month_by_continents_un_normalized.png)    |
|:---------------------------------------------------------:|
| *Month-of-birth distribution, by continent (normalized).* |

|      ![](res/quarter_by_continent_un_normalized_2.png)      |
|:-----------------------------------------------------------:|
| *Quarter-of-birth distribution, by continent (normalized).* |

**Conclusion:**
- The continents mainly represented in the two datasets (ITU and UN) share **very similar month-of-birth and quarter-of-birth distributions**.
- Therefore, the difference in continent distributions **does not explain the discrepancy** in month-of-birth and quarter-of-birth distributions between the ITU and UN datasets.

</details>

---

<details>
  <summary>Click to expand - 🎂 <strong>Age distribution of World Triathlon athletes used for this analysis.</strong></summary>

The UN and ITU datasets share the **same average age (25)**, but the **ITU age distribution is not uniform**, unlike the UN one.
- Importance sampling could be applied to the UN dataset to make the two distributions match, but I would be very surprised if that had an **impact on the overall conclusion**. 

|                    ![age.png](res/age.png)                    | 
|:-------------------------------------------------------------:| 
| *Age of athletes considered for the month-of-birth analysis.* |

</details>

---

> _Is the difference between ITU and UN month- and quarter-of-birth distributions **statistically significant**?_

<details>
  <summary>Click to expand - 🧮 <strong>Statistical test.</strong></summary>

**3,439 birth entries** have been collected (**"observed"**) from the World Triathlon (formerly **ITU**) data.
- A priori there is **no link** between the **quarter-of-birth** and the **fact of being a high-level triathlete**.
- Therefore, it can be **assumed** that the ITU observations **follow the UN distribution**.

From the UN distribution, the **expected** number of births for each quarter is computed:

|    |  OBSERVED (ITU)  |  EXPECTED (UN)  |
|:--:|:----------------:|:---------------:|
| Q1 |       987        |     854.443     |
| Q2 |       859        |     845.248     |
| Q3 |       820        |     893.717     |
| Q4 |       773        |     845.592     |

The number of births in the **two columns look very different**: more observations than expected for `Q1`, fewer for `Q3` and `Q4`.
- The situation is similar to the case of a **6-sided dice**, which is **suspected to be biased**. :game_die:
  - After rolling the die many times and counting each outcome, one can ask:
  - _Is just due to **randomness** or is it because the **dice is unfair**?_

Back to our problem:
- How to **quantify the deviation** between the two columns?

|    |  OBSERVED (ITU)  |  EXPECTED (UN)  |   DIFF   |  DIFF^2  |  DIFF^2 / EXPECTED  |
|:--:|:----------------:|:---------------:|:--------:|:--------:|:-------------------:|
| Q1 |       987        |     854.443     | 132.557  | 17571.3  |       20.5646       |
| Q2 |       859        |     845.248     | 13.7516  | 189.106  |      0.223728       |
| Q3 |       820        |     893.717     | -73.7166 | 5434.14  |       6.08039       |
| Q4 |       773        |     845.592     | -72.5916 | 5269.54  |       6.23178       |

One can compute the **differences between columns**, square them to ensure they are positive, normalize them and **sum the results**:
- `SUM OF [DIFF^2 / EXPECTED]` = `20.5646 + 0.2237 + 6.0804 + 6.2318` = **`33.10`**
- It `33.10` large? What does it mean? What can be concluded?

There is a mathematical formula that, given this computed number (`33.10`), answers the following question:
- _What is the **probability of observing such a discrepancy (`33.10`)** or an even larger one, **assuming** that the **ITU data should follow the UN** quarter-of-birth distribution?_
- In other words: _How likely is it that **the observed deviation** is due to **random chance**?_

For `33.10`, the formula gives `p = 0.0000003`, i.e. `0.00003%`.

**Conclusion:**
- The extremely low probability (`0.00003%`) indicates that the **observed differences** in quarters-of-birth among World Triathlon athletes are **highly unlikely to be due to random chance**.
- Therefore, the observed differences are **statistically significant**.
- This suggests a **systematic deviation from the expected UN distribution**.
- In other words, the quarters-of-birth of high-level triathletes **do not align with the general population** as represented by the UN distribution.

For more details about the derivation:
- An [article by Matteo Courthoud](https://matteocourthoud.github.io/post/chisquared/) to understand the [Chi-square test](https://en.wikipedia.org/wiki/Chi-squared_test).

</details>

---

:warning: These findings **do NOT indicate** that _"World Triathlon athletes born in January **are more performant** than others born in later months"_!
- This birth-of-month analysis rather shows that **someone born earlier** in one year **is MORE LIKELY TO BECOME PRO TRIATHLETE** than one born later in the same year.

Here is one **possible explanation**:
- Kids born on **January, 1st and December 31st** of the same year compete in the **same age category**.
- For example, at the age of 12, a 12-month difference represents **10% of their lifetime**.
- A 12-year kid born in January could, in theory, be ~10% **physically more developed (in terms of strength and stamina)** than one born in December.
- This **edge** could give an advantage to kids and teenagers born in the first months of a year during their early **races in youth categories**.
- They are **more likely** to **perform well, stand out, gain experience, and get selected for international competitions**, eventually **becoming professional**. :trophy:
  - Similar to a snowball effect. :cyclone:
- This phenomenon, known as [**relative age effect**](https://en.wikipedia.org/wiki/Relative_age_effect), was also observed on young Spanish triathletes by [Ferriz et al.](https://www.mdpi.com/2071-1050/12/17/6792) in 2020.

---

---

# :weight_lifting: BODY MASS INDEX

> "The [BMI](https://en.wikipedia.org/wiki/Body_mass_index) is defined as the **body mass** divided by the **square of the body height**, and is expressed in units of kg/m^2"

To maximize the amount of data, **all athletes registered with World Triathlon** are considered (not just those participating in world-cups and world-series).
- In total, **504 athletes** aged between 15 and 53 (average is 27) are included.

| ![bmi.png](res/bmi.png) | 
|:-----------------------:| 
|   *Body Mass Index.*    |

| ![weight_height.png](res/weight_height.png) | 
|:-------------------------------------------:| 
|           *Weights and Heights.*            |


First, is the BMI a **relevant metric** here? No!
- It is useful for public health, providing a quick and simple measure to identify **trends in obesity and underweight conditions**.
- But **it does not measure fitness levels, physical endurance, strength, flexibility, or other aspects of physical health**.
- Many athletes may have a high BMI due to increased **muscle mass**, yet they are fit and healthy.

Second, there is no enough data.
- **Only 14%** of athletes registered with World Triathlon have valid weight and height information (504 out of 3560).
- Most athletes did not input their dimensions.
- Sometimes for privacy reasons, e.g. the entry for Kristian Blummenfelt's ( :norway: ) weight: _"None of your business"_.

Third, some data may be outdated.
- The body weight that can **vary during a career** (many athletes enter the database as juniors) or even during a season.

Alternative metrics such as _Body Fat Percentage_ or _Muscle Mass Percentage_ would be more appropriate for **fitness assessment**.

If **not much can be concluded**, comparing oneself to the distributions can still be interesting.

<details>
  <summary>Click to expand - 📏 <strong>Non-standardized data format!</strong></summary>

Here are examples of `height` data. :straight_ruler:

```
 '6 Foot',
 "194, 6'4",
 '1.76 mts',
 '62 kg ',
 '1.80 meters',
 '174m',
 '5\'2"',
 '165 cms',
 '1,81 CM',
 '6ft. 2in.',
 '6ft 2in',
 '5’7”',
 '6 ft 0 in',
 '170cm/5.58ft',
 '57kg',
 '5.5ft',
 '1,77mts',
 'MT. 175',
 '164,4cm',
 '1.66 MTS',
 '5\'8"',
 '183 cm',
 "6'4",
 '1.9m',
 '6 Ft',
 "1'72",
 '186cm',
 '182',
 '180 ',
 '182CM'
```

And some `weight` data. :weight_lifting:
```
 'None of your business ',
 '160',
 '70 kg “in season “ ;-)',
 '1:68 m ',
 '140 lb',
 '51kgs ',
 '138 LBs',
 '1,78',
 '75 KG',
 '135ibs',
 '54kg/119lb',
 '42 kilo',
 '135IIbs',
 '187 lbs',
 'KG. 62',
 '49,4 kg',
 '67KG',
 '62 Kg',
 '175',
 '145lb',
 '52kg',
 '67',
 '140 Ibs',
 '65',
 '75 ',
 '66KG'
```

Interesting to see the **different units and formats**.

Some **processing and filtering** are required! :broom:

</details>

---

---

# :scroll: CONCLUSION

## :bulb: IDEAS

Here are **some ideas** for **data to explore**:

#### :mag: 1) MORE DETAILED RACES ANALYSES

As mentioned by Alex Yee in [this video](https://youtu.be/zoYeVlM28J4?t=689):

> "You are doing a **full gas effort** at the start of a race which is **2 hours long**. If you told somebody to do that on a marathon, they would laugh in your face."

World Triathlon data provides **a single time** for **each leg**: `swim`, `t1`, `bike`, `t2`, `run`. There is no detail about the pace evolution **during each segment**. For instance:
- Fast swim start to reach the first buoy.
- Fast bike start to break away or catch a pack.
- Fast run start - _I have never really understood the benefit compared to a steady effort._
- Fast run finish.

Some events, such as [Paris Olympics](https://olympics.com/en/paris-2024/results/triathlon/men-s-individual/fnl-000100--), offer **detailed results with lap times**.
- It is for instance very instructive to **compare the runs** of Alex Yee ( :gb: ), Hayden Wilde ( :new_zealand: ) and Léo Bergère ( :fr: ).
- The first two completed the **first 1050m in `2:42`**.
- Alex Yee then "slowed down" to ~`3:00` for the following three laps, while Léo Bergère was **a bit more regular**: `2:49`, `2:56`, `3:01`, `2:54`.
- Such data should be very interesting to analyse.

In addition to **paces**, it would be interesting to access **data** such as:
- Swim **stroke rate**.
- Bike **power** and cadence.
- Run **cadence**.
- Run **maximum speed** during the sprint.
- **Heart rate**.
- ...
- For comparison, heart rate information from some athletes is shown in UCI mountain-bike world-cups videos.

**Activity trackers** would be needed for these recordings, but athletes **rarely wear them** while racing, making **swim** and **run data recording** difficult.
- _This is also something I find puzzling: such data should be **invaluable for elite athletes**, shouldn't it?_ 
  - I first thought it was **forbidden** during the swim. [**World Triathlon rules**](https://www.triathlon.org/about/downloads/category/competition_rules) are **not very clear** to me:
    - _"Athletes may not use **communication devices** of any type, including but not limited to cell phones, **smart watches** ..."._
    - _"Propulsion devices that create an advantage for the athlete, or a risk to others, are forbidden."_ _Could a sport-watch increase the propulsion surface or be harmful to others in case of contact?_
    - On the other hand, the **swim section** states: _"**Electronic devices may be used** in the **competition** unless they are distracting the athlete from paying full attention to their surroundings"_.
- There are a few exceptions, where devices are used either for **assisting athletes in pacing their runs** or for **recording data**, such as:
  - Cassandre Beaugrand ( :fr: ) [seen **holding some device** during the Paris Olympics](https://www.francetvinfo.fr/pictures/S730frivHusOjCabDZvitrL_1z8/0x106:1024x682/1328x747/filters:format(avif):quality(50)/2024/07/31/000-36776ev-66aa06e0cbb4b034364713.jpg) and [wearing one on her wrist at Gagliari 2024 ( :it: ), where Beth Potter ( :gb: ) also appeared to be using one](https://youtu.be/vFV-kB8727I?t=189). _Possibly to pace her 10k run?_
  - Hayden Wilde ( :new_zealand: ), [spotted using **a device** during the Paris Olympics](https://www.triathlon.org/uploads/hrgalleries/191104/awag1132_paris2024__medium.jpg) _(discussion [here](https://the5krunner.com/2024/08/01/alex-yee-paris-gold-with-coros-dura-plus-what-was-haydn-wilde-looking-at-during-the-run/))_, and at [Gagliari 2023 ( :it: )](https://triathlon.org/results/result/2023_world_triathlon_championship_series_cagliari/586471) where [he did not wear a watch during the swim](https://triathlon-uploads.imgix.net/webgalleries/174957/tzaf5501.jpg?w=1140&auto=format), but [**had one for the run**](https://triathlon-uploads.imgix.net/webgalleries/174957/tomz0840.jpg?w=1140&auto=format) _(possibly attached with [an elastic band](https://www.youtube.com/watch?v=eyliQoQskww&t=3)?)_, which [he **stopped at the finish line**](https://triathlon-uploads.imgix.net/webgalleries/174957/tomz0987.jpg?w=1140&auto=format).
  - The Australian team ( :australia: ) at [Hamburg 2017 ( :de: )](https://triathlon.org/events/event/2017_hamburg_itu_triathlon_mixed_relay_world_championships) with **sensors taped to their backs**: [image 1](https://content.api.news/v3/images/bin/59304654a9f11b7e563cdab4e0e892d6?width=1024), [image 2](https://triathlon-uploads.imgix.net/webgalleries/112903/170716-itu-hamburg-team-web-msj-022.jpg?w=1140&auto=format), [image 3](https://triathlon-uploads.imgix.net/webgalleries/112903/170716-itu-hamburg-team-web-msj-047.jpg?w=800&). _What did they measure?_
- The **GPS features** of activity trackers could also provide **more precise estimations of the course distances**.
  - Especially for the **run**, and even for the **swim, to compare the trajectories**.
- Some athletes seem to use **heart rate monitor (HRM) belts**, such as [Kristian Blummenfeld ( :norway: ) at Tokyo 2021 ( :jp: )](https://triathlon.org/news/article/kristian_blummenfelt_crowned_tokyo_2020_olympic_champion).
  - But as far as I know, no **stroke rate**, **cadence** or **GPS** data can be recorded with these devices.

**Strava** could be used to retrieve activities:
- Many athletes **publish** their activities there, either their races (often limited to the bike section) or training sessions.
- However, as mentioned, almost **no swim or run** information is recorded during **races**.

#### :shopping: 2) EQUIPMENT CHOICE

What is the **best wetsuit**? What are the **fastest running shoes**?
- There are already some tests and reports conducted by researchers.
- However, I believe that **examining athletes' preferences** would provide **more reliable and valuable** results.

Not all athletes are **sponsored** by swimming or running brands.
- Therefore, many have the **freedom** to **experiment, compare, and choose** the equipment **they believe will enhance their performance**.
- As an example, one could track how many athletes wore Asics, Adidas, Nike, New Balance, etc., at major events, noting the models used, and **exclude those provided by sponsors**.

_I recall reading about a similar project but can no longer find the reference._

#### :moneybag: 3) MONEY

It would be interesting to investigate the **financial aspects** of the competitions, such as:
- The **prize money** for the different World Triathlon race categories.
- The event **registration costs**.
- Eventually, to estimate **from which rank an athlete can make a descent living**. (Of course, sponsoring and federation support also play a role).

#### :spaghetti: 4) MISCELLANEOUS

- Analyse the **correlation** between **transition ranking** and **finish ranking**.
  - Especially for T2.
- Compare **WTCS** and **world-cups** more thoroughly.
  - These two event-categories have been combined in several sections of this document to **increase the dataset size** and hopefully improve statistical significance.
  - However, in some cases this approach may not be optimal, and it would be insightful to explore the differences between these categories.
  - The level is **generally higher on world series**, but there are some exceptions: **World cups** like [2020 Arzachena ( :it: )](https://www.triathlon.org/results/result/2020_arzachena_itu_triathlon_world_cup/352548), [2014 New Plymouth ( :new_zealand: )](https://www.triathlon.org/results/result/2014_new_plymouth_itu_triathlon_world_cup/264274), [2014 Mooloolaba ( :australia: )](https://www.triathlon.org/results/result/2014_mooloolaba_itu_triathlon_world_cup/264271) and **[2009](https://www.triathlon.org/results/result/2009_hy-vee_itu_triathlon_elite_cup/5187)** and [2010 **Des Moines ( :us: )**](https://www.triathlon.org/results/result/2010_hy-vee_itu_triathlon_elite_cup/5613) **likely matched** the **competition level** of the average World Triathlon Series events. In fact, they were probably more competitive than some WTCS races held during Olympic years, such as [2012 Sydney ( :australia: )](https://www.triathlon.org/results/result/2012_itu_world_triathlon_sydney/7599), [2016 Cape Town ( :south_africa: )](https://www.triathlon.org/results/result/2016_itu_world_triathlon_cape_town/280877), [2021 Hamburg ( :de: )](https://www.triathlon.org/events/event/2021_world_triathlon_hamburg), [2024 Hamburg ( :de: )](https://www.triathlon.org/results/result/2024_world_triathlon_championship_series_hamburg/627964).
  - Compared to the early 2010s, world-cups _(possibly due to their location, date, and low prize money?)_ appear to have been largely abandoned by top athletes in favor of newer race formats, such as the [supertri](https://supertri.com/), the [French Grand Prix](https://en.wikipedia.org/wiki/Grand_Prix_de_Triathlon) and even Ironman races.
- The [arbitrary decision to focus on the **top 5-9**](#books-data) was made to capture a stable and consistent **representation of the general competitive field**.
  - However, examining the **top performance** (e.g. top-1 or top-3) or using a **broader range** could also yield valuable insights.
- Conduct advanced analyses of **cycling performances** would be interesting.
  - Additional data may be required: drawing conclusions based solely on **bike split times** is challenging, due to the influence of **drafting** and pack dynamics.
- Investigate the impact of **swim conditions** on swim performance and race dynamics.
  - Including **water temperature**, presence of **waves**, and **salinity**.
- Take a closer look at the **critical start of the bike segment**.
  - For example: _Given a lag at T1, how likely is it to catch the first group?_
- Understand the system of **penalties** and their impact on race dynamics.
  - The 2024 Paris Olympics ( :fr: ) saw a surprising number of penalties: **[6 women out of 51](https://triathlon.org/results/result/paris_2024_olympic_games/655048) and [10 men out of 50](https://triathlon.org/results/result/paris_2024_olympic_games/655047)** received a **15s penalty**.
  - Before focusing on gaining seconds, some athletes may need to **prioritize avoiding penalties**, such as by **correctly timing their dive** and making sure to **place their helmet inside** the transition box.
- Analyze the **trajectory** of successful elite athletes.
  - _How did they perform as juniors, and how did they **progress** from **junior** to **U23** to **elite**?_
  - One could also ask: _One junior athlete excels in swimming, another one in running. Which is more likely to become an Elite and perform in this category?_
- Try to estimate the **level of a race**.
  - Propose a **formula** based on metrics such as the ranking of participating athletes and, if available, their results in this race.
    - Extensions include evaluation of individual race segments (swim, bike, run), and **athlete scoring**.
  - Potential **pre-race and post-race applications**:
    - _What performance objectives should the **coach** set, considering the expected race difficulty?_
    - _Should a **federation** select an athlete for this event based on the competitiveness of the start list?_
    - _How strong are the best swimmers for this race? Who would be the optimal neighbours on the **start pontoon**?_
    - _How strong was this top-10 finish, given the competition level? Did an athlete **overperform or underperform** in a specific leg?_
    - _What are the most hotly contested races?_ With a formula like this, I could **classify the races by level** and keep only the e.g. 100 most disputed for my analyses.
- ...

---

## :computer: CODE

The **python code** to fetch the data, set the parameters and generate plots is available in [this GitHub repository](https://github.com/chauvinSimon/tri_stats). There are **two ways to use it**:

- Either **locally**, if you are familiar with **python**. :snake:
  - Clone the repo and install the required python packages. 
  - [Create a key for the World Triathlon API](https://apps.api.triathlon.org/register) and add it to a `api_key.txt` file to save in `tri_stats/`.
  - Run the different scripts of `tri_stats/scripts`.
- Or in the **cloud**, using **free** tools: **Google Colab** and **Google Drive**. :v:
  - _[Only once]_ _[Recommended]_ Create a Google account, to be used only for this project.
  - _[Only once]_ Open **https://colab.research.google.com/github/chauvinSimon/tri_stats/**, and click on `notebooks/main.ipynb`.
  - _[Only once]_ Click **`Copy to Drive`** _(if hidden, `Toggle header visibility`)_, and then `Open in a new tab`.
  - _[Every time]_ In the copied version (saved by defaults as `Copy of main.ipynb`, at https://drive.google.com/drive/my-drive, under `My Drive / Colab Notebooks`), follow the instructions.

---

## :takeout_box: TAKEAWAYS

:warning: Most **summary numbers** given in this section are **AVERAGES**.
- For instance **race-averages** are computed from the 5th to 9th best times of **each leg**, and sometimes **averaged** over multiples years.

Here are some simplified **key takeaways**:
- :stopwatch: The three sports account for **16.4%** ( :swimmer: ), **53.1%** ( :bicyclist: ), **28.9%** ( :runner: ) of the overall time. Transitions for 1.1% and 0.5%. [[link]](#question-three-sports)
- :athletic_shoe: While **swim and bike paces are similar** between sprint and olympic formats, the **10k run** requires **7 s/km** more than the 5k. [[link]](#stopwatch-paces)
- :swimmer: Women swim at **1:18 / 100m**, men at **1:12 / 100m**. [[link]](#couple-women-vs-men)
- :bicyclist: Women ride **4 km/h slower**, at **37.4 km/h**, compared to men at **41.4 km/h**. [[link]](#couple-women-vs-men)
- :runner: Women run the 10k at **3:33 min/km** (3:26 for 5k), men at **3:07 min/km** (3:00 for 5k). [[link]](#couple-women-vs-men)
- :shower: The time charged to the **wetsuit during the T1** transition is **~9s**. [[link]](#shower-wetsuit-at-t1)
- :couple: **Women swim 8.8% slower** than men with the same equipment. They also **ride 10.6%** and **run 14.2%** slower. [[link]](#focus-on-the-swim-swimmer)
- :chart_with_downwards_trend: The **women/men difference has not significantly reduced** on the years, except for the run leg of the sprint-format races (-0.13 % / year) and for the swim of WTCS (-11 % / year). [[link]](#couple-women-vs-men)
- :penguin: There is **no evidence that wetsuits reduce swim gaps** between top and less competitive swimmers. [[link]](#swimmer-swim-gaps)
- :one_piece_swimsuit: Swim is **4-5% faster with wetsuit**. [[link]](#penguin-wetsuit-benefit)
- :fr: The **swim** of 2024 Paris Olympics was **unusually long** (more than **2:30 longer**), probably because of the current in La Seine. In particular, the 5-9th women swam **more than 1:30 / 100m**. [[link]](#spiral_calendar-level-over-years)
- :zap: Winning by a **run comeback**, i.e. after not ending the bike in the front group, is entertaining but **rare** in the olympic format (28% for men and 7% for women) and is getting even rarer. [[link]](#dart-race-scenario)
- :bicyclist: The **size of the front group** after bike averages around **15**. It decreases to 4 or fewer (**small breakaway**) in about **1/4 of women's** and **1/3 of men's** olympic-races. [[link]](#dart-race-scenario)
- :athletic_shoe: Over **2/3 of races** are won by the **best runner**. [[link]](#runner-how-often-does-the-best-runner-win-trophy)
- :camera_flash: In men's races, **17%** (sprint format) and **10%** (olympic) are **won by a sprint finish**, occurring **50% more often** than in women's races. [[link]](#rocket-sprint-finish)
- :woman_cartwheeling: Women's races occasionally feature **wins by very large margins**. [[link]](#rocket-sprint-finish)
- :straight_ruler: The gaps between the **winner and the second** are, on average, **twice as large** in olympic formats compared to sprint formats, and **twice as large** for women compared to men. [[link]](#rocket-sprint-finish)
- :rocket: **Bike** and **run** times in WTCS olympic races have reached **all-time lows**. [[link]](#spiral_calendar-level-over-years)
- :penguin: The wetsuit is allowed in **~1/3 of races**. More often for women (37%) than for men (32%). [[link]](#penguin-wetsuit-benefit)
- :thermometer: Athletes must compete in a **variety of conditions**: Notably, 80% of the **recorded air temperatures** (lower estimates) fall between **17°C** and **30°C** and almost uniformly so. [[link]](#thermometer-temperatures)
- :hot_face: **Heat** tends to **slow down** running pace. [[link]](#parasol_on_ground-air-temperatures-and-run-times)
- :calendar: On average, athletes raced **10 times** (world cups and WTCS) in 2019 and 2023, compared to **6 times in 2009**. [[link]](#athlete-seasons)
- :calendar: Their World Triathlon sprint- and olympic-distance season has extended from **130 days** in 2009 to **200 days** in 2023. [[link]](#calendar-season-duration)
- :ticket: The limit of **3 athletes per nation** for the Olympics creates challenges for the highly represented nations such as :us:, :gb:, :australia:, :de: and :fr:. [[link]](#earth_africa-athlete-nations)
- :birthday: Athletes finishing 5th-9th are, on average, **between 26 and 28** years old. [[link]](#baby-age)
- :checkered_flag: Women and men typically race their last world-cup or WTCS at an average age of **31 years**, thought there are significant variations. [[link]](#checkered_flag-age-of-last-race)
- :bar_chart: Someone **born earlier in the year** is **more likely** to become professional triathletes compared to those born later in the same year. [[link]](#date-month-of-birth)

---

**Thank you for reading until the end!**
- If you have any questions, suggestions, corrections, or comments, please feel free to contact me at `simon.chauvin.contact[at]gmail.com`.
- Cheers,
- Simon :smiley:
