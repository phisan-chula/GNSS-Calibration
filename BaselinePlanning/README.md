## GNSS Baseline Planning

Project:   Pangna Rock Art Project  
PointKML:  Ancient_painting.kml  
Receivers:  ['CHC-1', 'CHC-2']  
Work Hour:  08:00 16:30  
transport time:  60 minutes  
Plotting baseline ./CACHE/RockArt_Baseline.gpkg ...  

### Table : Associated NCDC CORS stations.
|    | STA   |               X |               Y |               Z | epoch            |
|---:|:------|----------------:|----------------:|----------------:|:-----------------|
|  3 | ATRG  |    -1044225.206 |     6238038.716 |      820026.993 | ITRF2014@2021.93 |
| 54 | NKBI  |    -1004107.392 |     6237146.359 |      874718.702 | ITRF2014@2021.93 |
| 72 | TPKT  |     -914875.254 |     6247977.495 |      896544.383 | ITRF2014@2021.93 |
| 82 | AWLK  |     -956898.469 |     6237553.731 |      923074.176 | ITRF2014@2021.93 |
![alt text](https://github.com/phisan-chula/GNSS-Calibration/blob/main/BaselinePlanning/Baseline_AWLK_TPKT.png)
![alt text](https://github.com/phisan-chula/GNSS-Calibration/blob/main/BaselinePlanning/Baseline_NKBI_ATRG.png)

### Case : 2 receivers "CHC-1" and "CHC-2"
### Table : Sessions for GNSS occupation 
|    | Loop    |   Day | Begin   | End   |   Duration | CHC-1   | CHC-2   |
|---:|:--------|------:|:--------|:------|-----------:|:--------|:--------|
|  0 | Aowluke |     1 | 08:00   | 08:20 |         20 | P-19    | P-20    |
|  1 | Aowluke |     1 | 09:20   | 09:44 |         24 | P-20    | P-23    |
|  2 | Aowluke |     1 | 10:44   | 11:05 |         21 | P-23    | P-21    |
|  3 | Aowluke |     1 | 12:05   | 12:25 |         20 | P-21    | P-22    |
|  4 | Aowluke |     1 | 13:25   | 13:54 |         29 | P-22    | P-26    |
|  5 | Aowluke |     1 | 14:54   | 15:14 |         20 | P-26    | P-27    |
|  6 | Aowluke |     1 | 16:14   | 16:34 |         20 | P-27    | P-25    |
|  7 | Aowluke |     2 | 08:00   | 08:22 |         22 | P-25    | AWLK    |
|  8 | Aowluke |     2 | 09:22   | 09:42 |         20 | AWLK    | P-12    |
|  9 | Aowluke |     2 | 10:42   | 11:02 |         20 | P-12    | P-28    |
| 10 | Aowluke |     2 | 12:02   | 12:22 |         20 | P-28    | P-13    |
| 11 | Aowluke |     2 | 13:22   | 13:42 |         20 | P-13    | P-16    |
| 12 | Aowluke |     2 | 14:42   | 15:02 |         20 | P-16    | P-15    |
| 13 | Aowluke |     2 | 16:02   | 16:22 |         20 | P-15    | P-14    |
| 14 | Aowluke |     2 | 17:22   | 17:42 |         20 | P-14    | P-17    |
| 15 | Aowluke |     3 | 08:00   | 08:20 |         20 | P-17    | P-18    |
| 16 | Aowluke |     3 | 09:20   | 09:40 |         20 | P-18    | P-19    |
| 17 | Aowluke |     3 | 10:40   | 11:00 |         20 | P-19    | P-20    |
| 18 | DOH44   |     3 | 12:00   | 12:22 |         22 | P-23    | P-24    |
| 19 | DOH44   |     3 | 13:22   | 13:51 |         29 | P-24    | P-29    |
| 20 | DOH44   |     3 | 14:51   | 15:41 |         50 | P-29    | P-26    |
| 21 | Lanta   |     3 | 16:41   | 17:16 |         35 | NKBI    | P-30    |
| 22 | Lanta   |     4 | 08:00   | 08:47 |         47 | P-30    | P-33    |
| 23 | Lanta   |     4 | 09:47   | 10:07 |         20 | P-33    | P-31    |
| 24 | Lanta   |     4 | 11:07   | 11:27 |         20 | P-31    | P-32    |
| 25 | Lanta   |     4 | 12:27   | 13:33 |         66 | P-32    | P-35    |
| 26 | Lanta   |     4 | 14:33   | 15:08 |         35 | P-35    | P-34    |
| 27 | Lanta   |     4 | 16:08   | 16:54 |         46 | P-34    | ATRG    |
| 28 | Punyee  |     5 | 08:00   | 08:47 |         47 | TPKT    | P-6     |
| 29 | Punyee  |     5 | 09:47   | 10:07 |         20 | P-6     | P-9     |
| 30 | Punyee  |     5 | 11:07   | 11:27 |         20 | P-9     | P-10    |
| 31 | Punyee  |     5 | 12:27   | 12:55 |         28 | P-10    | P-1     |
| 32 | Punyee  |     5 | 13:55   | 14:15 |         20 | P-1     | P-4     |
| 33 | Punyee  |     5 | 15:15   | 15:35 |         20 | P-4     | P-5     |
| 34 | Punyee  |     5 | 16:35   | 16:55 |         20 | P-5     | P-3     |
| 35 | Punyee  |     6 | 08:00   | 08:20 |         20 | P-3     | P-2     |
| 36 | Punyee  |     6 | 09:20   | 09:40 |         20 | P-2     | P-8     |
| 37 | Punyee  |     6 | 10:40   | 11:00 |         20 | P-8     | P-7     |
| 38 | Punyee  |     6 | 12:00   | 12:20 |         20 | P-7     | P-11    |
| 39 | Punyee  |     6 | 13:20   | 13:40 |         20 | P-11    | P-6     |
| 40 | link-1  |     6 | 14:40   | 15:19 |         39 | P-1     | P-14    |
| 41 | link-2  |     6 | 16:19   | 16:57 |         38 | P-10    | P-19    |

### Case : 3 receivers "HAXX" , "CHC-1" and "CHC-2"
Receivers:  ['HAXX', 'CHC-1', 'CHC-2']
Work Hour:  08:00 to 16:30
Transport time:  60 minutes
Plotting baseline ./CACHE/RockArt_Baseline.gpkg ...
### Table : Sessions for GNSS occupation
=========================== GNSS Occupation Session ========================
|    | Loop    |   Day | Begin   | End   |   Duration | HAXX   | CHC-1   | CHC-2   |
|---:|:--------|------:|:--------|:------|-----------:|:-------|:--------|:--------|
|  0 | Aowluke |     1 | 08:00   | 08:24 |         24 | P-19   | P-20    | P-23    |
|  1 | Aowluke |     1 | 09:24   | 09:45 |         21 | P-23   | P-21    | P-22    |
|  2 | Aowluke |     1 | 10:45   | 11:14 |         29 | P-22   | P-26    | P-27    |
|  3 | Aowluke |     1 | 12:14   | 12:36 |         22 | P-27   | P-25    | AWLK    |
|  4 | Aowluke |     1 | 13:36   | 13:56 |         20 | AWLK   | P-12    | P-28    |
|  5 | Aowluke |     1 | 14:56   | 15:16 |         20 | P-28   | P-13    | P-16    |
|  6 | Aowluke |     1 | 16:16   | 16:36 |         20 | P-16   | P-15    | P-14    |
|  7 | Aowluke |     2 | 08:00   | 08:20 |         20 | P-14   | P-17    | P-18    |
|  8 | Aowluke |     2 | 09:20   | 09:40 |         20 | P-18   | P-19    | P-20    |
|  9 | DOH44   |     2 | 10:40   | 11:09 |         29 | P-23   | P-24    | P-29    |
| 10 | DOH44   |     2 | 12:09   | 12:59 |         50 | P-29   | P-26    |         |
| 11 | Lanta   |     2 | 13:59   | 14:46 |         47 | NKBI   | P-30    | P-33    |
| 12 | Lanta   |     2 | 15:46   | 16:06 |         20 | P-33   | P-31    | P-32    |
| 13 | Lanta   |     2 | 17:06   | 18:12 |         66 | P-32   | P-35    | P-34    |
| 14 | Lanta   |     3 | 08:00   | 08:46 |         46 | P-34   | ATRG    |         |
| 15 | Punyee  |     3 | 09:46   | 10:33 |         47 | TPKT   | P-6     | P-9     |
| 16 | Punyee  |     3 | 11:33   | 12:01 |         28 | P-9    | P-10    | P-1     |
| 17 | Punyee  |     3 | 13:01   | 13:21 |         20 | P-1    | P-4     | P-5     |
| 18 | Punyee  |     3 | 14:21   | 14:41 |         20 | P-5    | P-3     | P-2     |
| 19 | Punyee  |     3 | 15:41   | 16:01 |         20 | P-2    | P-8     | P-7     |
| 20 | Punyee  |     3 | 17:01   | 17:21 |         20 | P-7    | P-11    | P-6     |
| 21 | link-1  |     4 | 08:00   | 08:39 |         39 | P-1    | P-14    |         |
| 22 | link-2  |     4 | 09:39   | 10:17 |         38 | P-10   | P-19    |         |


