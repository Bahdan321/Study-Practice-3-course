import flet as ft


def main(page: ft.Page):

    anime_list = [
        {
            "title": "Киберпанк: Бегущие по краю",
            "poster": "https://kinopoisk-ru.clstorage.net/Q152b2H31/3be82betF/9vzxE-f2-w8mL8r8TpKzfXuf9_OYwY-lxyoTkWieGdARYAxyOXsIKFsV-GNXpZ5uozVrGz44Ltv1_6RsCameYMf1pAqyirNWd2KygC_Xz3wv5sKG1cn-hIo6Z9wp52Vs0cDE1_Hj9IjbpH1uRrnrG8ZIahJDUHeSyOq5pb34dr36zLUHN7byF1ITp4CuUle9D2rHA1Cwfw0XM099lB4dBKUA4IfJ_5wcl6yBJorcX4-y3IaGl0iro8zmeels5O51NgRV90eG8guanzOAZhpfxXPuS2e4jFM123NDbSiCGaRhUARzPQ-MKFscCfq6rM-zivgebme8N-M0KsVdTMjKXX6sbfPnjrKLFpuPaIpWR6kvxpd_hCz_9Zff_5UQqnGgkZig46G7oBTPUK0uirjHD4JcnnqXNPvzTH7JfSiY5tWyTKUHJ4p-465zK2S-ygcJj2pvj6Bcq93XI49dBHK1KDVw4HdVZywcl2QFerbs5wt2-B56UzDj47ieMRFMuN71NnRd90_mqp_Kl0sMosIDhX-2d5dYjJN5Wzdn7UByjYiFXNRnobfYvM8s7W4WJLd70rzO6tfQEx84Znl95CzmtbYE1cdrpjLvMleDcD6-261_cufTqNC_qbtbx7lQlm0cASxkN5G77OBP2N0esijvU0bkgh73cKM79L6x9fzMxt2ilNWnR5YSm0Zf5yyeEqf1y6qfUzCUn6V3p4vlAO6hvKkAbDdRN9Q4r0ih4n7gj9eyRBaK33wz2zCyJYkkNGJ1VpTB-zOSght6_89YhoK7Df-228NUBPuV1x_j2ShuGUgVfGj_6VuYoO9QDYZGSH9zbiy2fkskP4_MskldBGzqpfa42fvvFia7yiPL2JYuS717JlP7qMR3HQMTe_l8fmFMBdjgx5FzYASXUIUKyigzE17IdoJ3WK-7UPpxVSjUvqEShGnLO7Y6BwL3j0iKMqeNQ0IHx2SAa627y7c5WB4RRIEYbEfNUxCU5wSBEp48_5_qfG7K2-grK1QCQTkcWNrFpmi9x-fyUmPScytMAi7jTQdi85Mg9Jdh59MbYfB2ecCZrADHCec0GO_kaX7eKG8rAlRmEsdQq-vYboWdBDTC9TYQuX_rHoKHMo8zYGJyp8W7wosDFMTnkZdzkxWs9j3cmXx41y2fMJgPPKU62jwH41bAdgpPJAt7GAKxMVjssr3iqNlHLwoiA4I3Y-geDr_pQ0J_n1QMe2XXs_NpAP45WHlIxHNtd1xMcxhd9sZAcx9exLLaP7AH5_j-zTnwZNIdImDR3ycKhvMqe68Qvpqbtd9Kf_sQgBMB59fnjdgOFSAdcCRnXfMUqPM0gQpaoDNvBtDe-kskp29sdrnlkEQaqa6Q4dNLktKfTgtD9HYCK8XX0qf3IKxjoR_34zHwdkGc5QhYe7H7VISPFOH2trRnA4pYep631BPj-ErxGUQYUjHWzMGPJybqd4ILS3CaPlsx6yZ_86CoF4VftzvZZAKBtIXogNvR02TkUyhxupYg12tWzObiYySDdyRytYn4sB4dxihJFyOOGh-uV7dIhjbLIVNS--8k8KMZc8NH_chOMSi1lERrFe_0_Ps8DY5aaOtzJrzyYr-gK4OsltFVfDhOKeYUFYNfin6nQuNT7Mq-tzlnYuvXKDgnqZ8nE_kUZu34-aD0j6EHCDRDsCFWHtwbM9JIdkqfUL87ZDY9nciw8qG27M2Lp4JeH8brS2wO1o9hh5qTY2zU54GPK4dxyGah0Dn8HHNlNxTEY2gdvlrAT9Nu1J6en_DTB_zGBUEQuLZJkvRlXy9u_peyHw-AlgLDCWfuZ3e8CP8hS6Ojafw6eaB5yETLHfeUvJeU8Y5WJBvfoujq_muoI6vUQo1xDGBCGZZAXWfvIrJ3InubzEo-R8k_WgOvuAyXIQM74xEMvmFYzWTofxk3DHD_rOl2Jvj362rYhsYzKNPfKA5pVQy8-m0-EDn7R4Y67ybzj3Q-BmPp_8L_C4AouxlDJ4-dZEbhMH0IxNuFcyRIT9x58k4wtx-CbOoCe-CXd-SuVcmU8M6dZnxd1ycCfiNac-9oGrLfJTtW62fQTNudb1sbVUBycTh9rGwLwZfguGs4CSbS3OsXOrC-Xndoe2_MniE9ZDBquTpoqZNfDhobIgPvoOISU7FDRgN3LMi72Rt3H42YBmH09VD01wHrDBwDFHXqMqwXr-qgXspTJNv3IK41RfiY0lla7BGD55oqh1YrGwQK1tuhV8ZL27xIE2lDR4fVEIYdyJXQ-Le5a2gEcyCBkkKou1MGPH527ygXL6CSaX2ooAZ1EgBFl9M6Luc6gztkuqYz3UPK98fkcLtRz99jLdTOlSS9UKDPMX9sPKfEoYpK-LuXNmziCtvAB2vctmkdyKT2tZK01etLAiZvTjfLwApyD8FfbiejFLzbdQdb--XcDqksmRgU1wUHgGjPTG1m2tDDh_YkTra_MJ93pH49_ajsHhHuoLEfvyI-I_rnD3i-Xs-pS04Pi5TwB6mHP-ulXAJl9JHshHO1VzCIJ8jx7k6ssx9CUM7-x0Cbf3zqUUXgyIoRSsxhezc6UiuO2yvgypoPaedmA9tYLCclS-cjYRz-lfTJ1HCLHW-QFE_cyf6G-Fc_7qw2WutU03MwmjGZiPQe9Rp82Vcv5pZvjpuXCAaKF8GvXqsDLDyjoWcfB5nYzpUsnegAB-WbNMjjJEEiegTr-y7IQn7HuOcnbOrBTaCkAs3-FB1HxwaykzYTP1wCxmMh805Hn1wED21_z7spJDo9iJkA3H_ty4TkTxAdNtboz2_2JB4aO9QrL_wKwWlMxJ5lOvxRywOSFucapwPYtqoTMVMi72sYtHuVnzu7ofDuuUyx4FzL3RvYtFOkwXYu6N8TRijy-sd8i7MwbrXdqCwKMX4sPQO7EhK_LlsfBLaO29lDamdzLIQf_c_Dq4EUur2kCfjUy7l7OMxP3Mn2viyfEzbMCt4z3Af7uDpA",
            "release_date": "13 сентября 2022 года",
            "description": "Действия аниме-сериала происходят в будущем, в вольном мегаполисе Найт-Сити, расположенном на западе Северной Америки. Город страдает от повсеместной коррупции, многие люди одержимы высокими технологиями и разного рода кибернетическими имплантатами. Помимо этого, в нём также большие проблемы с преступностью, дискриминацией по разным признакам и безопасностью населения.",
            "opinion": "ABSOLUTE CINEMA",
        },
        {
            "title": "Как и ожидалось, моя школьная романтическая жизнь не удалась",
            "poster": "https://kinopoisk-ru.clstorage.net/Q152b2H31/3be82betF/9vzxE-f2-w8mL8r8TpKzfXuf9_OYwY-lxyoTkWieGdARYAxyOXsIKFsV-Hd7gbJWhxVqXx9lcu_ktvRsDbGecMf04Aa2ir4jF3azwWPP2jAmp6qG7ISihIo6Z9wp52Vs0cDE1_Hj9IjbpH1uRrnrG8ZIahJDUHeSyOq5pb34dr36zLUHN7byF1ITp4CuUle9D2rHA1Cwfw0XM099lB4dBKUA4IfJ_5wcl6yBJorcX4-y3IaGl0iro8zmeels5O51NgRV90eG8guanzOAZhpfxXPuS2e4jFM123NDbSiCGaRhUARzPQ-MKFscCfq6rM-zivgebme8N-M0KsVdTMjKXX6sbfPnjrKLFpuPaIpWR6kvxpd_hCz_9Zff_5UQqnGgkZig46G7oBTPUK0uirjHD4JcnnqXNPvzTH7JfSiY5tWyTKUHJ4p-465zK2S-ygcJj2pvj6Bcq93XI49dBHK1KDVw4HdVZywcl2QFerbs5wt2-B56UzDj47ieMRFMuN71NnRd90_mqp_Kl0sMosIDhX-2d5dYjJN5Wzdn7UByjYiFXNRnobfYvM8s7W4WJLd70rzO6tfQEx84Znl95CzmtbYE1cdrpjLvMleDcD6-261_cufTqNC_qbtbx7lQlm0cASxkN5G77OBP2N0esijvU0bkgh73cKM79L6x9fzMxt2ilNWnR5YSm0Zf5yyeEqf1y6qfUzCUn6V3p4vlAO6hvKkAbDdRN9Q4r0ih4n7gj9eyRBaK33wz2zCyJYkkNGJ1VpTB-zOSght6_89YhoK7Df-228NUBPuV1x_j2ShuGUgVfGj_6VuYoO9QDYZGSH9zbiy2fkskP4_MskldBGzqpfa42fvvFia7yiPL2JYuS717JlP7qMR3HQMTe_l8fmFMBdjgx5FzYASXUIUKyigzE17IdoJ3WK-7UPpxVSjUvqEShGnLO7Y6BwL3j0iKMqeNQ0IHx2SAa627y7c5WB4RRIEYbEfNUxCU5wSBEp48_5_qfG7K2-grK1QCQTkcWNrFpmi9x-fyUmPScytMAi7jTQdi85Mg9Jdh59MbYfB2ecCZrADHCec0GO_kaX7eKG8rAlRmEsdQq-vYboWdBDTC9TYQuX_rHoKHMo8zYGJyp8W7wosDFMTnkZdzkxWs9j3cmXx41y2fMJgPPKU62jwH41bAdgpPJAt7GAKxMVjssr3iqNlHLwoiA4I3Y-geDr_pQ0J_n1QMe2XXs_NpAP45WHlIxHNtd1xMcxhd9sZAcx9exLLaP7AH5_j-zTnwZNIdImDR3ycKhvMqe68Qvpqbtd9Kf_sQgBMB59fnjdgOFSAdcCRnXfMUqPM0gQpaoDNvBtDe-kskp29sdrnlkEQaqa6Q4dNLktKfTgtD9HYCK8XX0qf3IKxjoR_34zHwdkGc5QhYe7H7VISPFOH2trRnA4pYep631BPj-ErxGUQYUjHWzMGPJybqd4ILS3CaPlsx6yZ_86CoF4VftzvZZAKBtIXogNvR02TkUyhxupYg12tWzObiYySDdyRytYn4sB4dxihJFyOOGh-uV7dIhjbLIVNS--8k8KMZc8NH_chOMSi1lERrFe_0_Ps8DY5aaOtzJrzyYr-gK4OsltFVfDhOKeYUFYNfin6nQuNT7Mq-tzlnYuvXKDgnqZ8nE_kUZu34-aD0j6EHCDRDsCFWHtwbM9JIdkqfUL87ZDY9nciw8qG27M2Lp4JeH8brS2wO1o9hh5qTY2zU54GPK4dxyGah0Dn8HHNlNxTEY2gdvlrAT9Nu1J6en_DTB_zGBUEQuLZJkvRlXy9u_peyHw-AlgLDCWfuZ3e8CP8hS6Ojafw6eaB5yETLHfeUvJeU8Y5WJBvfoujq_muoI6vUQo1xDGBCGZZAXWfvIrJ3InubzEo-R8k_WgOvuAyXIQM74xEMvmFYzWTofxk3DHD_rOl2Jvj362rYhsYzKNPfKA5pVQy8-m0-EDn7R4Y67ybzj3Q-BmPp_8L_C4AouxlDJ4-dZEbhMH0IxNuFcyRIT9x58k4wtx-CbOoCe-CXd-SuVcmU8M6dZnxd1ycCfiNac-9oGrLfJTtW62fQTNudb1sbVUBycTh9rGwLwZfguGs4CSbS3OsXOrC-Xndoe2_MniE9ZDBquTpoqZNfDhobIgPvoOISU7FDRgN3LMi72Rt3H42YBmH09VD01wHrDBwDFHXqMqwXr-qgXspTJNv3IK41RfiY0lla7BGD55oqh1YrGwQK1tuhV8ZL27xIE2lDR4fVEIYdyJXQ-Le5a2gEcyCBkkKou1MGPH527ygXL6CSaX2ooAZ1EgBFl9M6Luc6gztkuqYz3UPK98fkcLtRz99jLdTOlSS9UKDPMX9sPKfEoYpK-LuXNmziCtvAB2vctmkdyKT2tZK01etLAiZvTjfLwApyD8FfbiejFLzbdQdb--XcDqksmRgU1wUHgGjPTG1m2tDDh_YkTra_MJ93pH49_ajsHhHuoLEfvyI-I_rnD3i-Xs-pS04Pi5TwB6mHP-ulXAJl9JHshHO1VzCIJ8jx7k6ssx9CUM7-x0Cbf3zqUUXgyIoRSsxhezc6UiuO2yvgypoPaedmA9tYLCclS-cjYRz-lfTJ1HCLHW-QFE_cyf6G-Fc_7qw2WutU03MwmjGZiPQe9Rp82Vcv5pZvjpuXCAaKF8GvXqsDLDyjoWcfB5nYzpUsnegAB-WbNMjjJEEiegTr-y7IQn7HuOcnbOrBTaCkAs3-FB1HxwaykzYTP1wCxmMh805Hn1wED21_z7spJDo9iJkA3H_ty4TkTxAdNtboz2_2JB4aO9QrL_wKwWlMxJ5lOvxRywOSFucapwPYtqoTMVMi72sYtHuVnzu7ofDuuUyx4FzL3RvYtFOkwXYu6N8TRijy-sd8i7MwbrXdqCwKMX4sPQO7EhK_LlsfBLaO29lDamdzLIQf_c_Dq4EUur2kCfjUy7l7OMxP3Mn2viyfEzbMCt4z3Af7uDpA",
            "release_date": "5 апреля 2013",
            "description": "Старшеклассник Хатиман Хикигая — интроверт, циник и пессимист. Он уверен, что дружба, любовь и прочие социальные отношения — полная чушь. После написанного Хатиманом уничижительного эссе, его в качестве наказания отправляют прямиком в клуб волонтёров, где ему придётся вместе с красавицей школы Юкино Юкиноситой решать проблемы других людей.",
            "opinion": "ABSOLUTE CINEMA",
        },
        {
            "title": "Моб Психо 100",
            "poster": "https://kinopoisk-ru.clstorage.net/Q152b2H31/3be82betF/9vzxE-f2-w8mL8r8TpKzfXuf9_OYwY-lxyoTkWieGdARYAxyOXsIKFsV-GNXpZ5uozVrMntxc6fgs4hsEbWPHMf04Cf2ir9yXjqyjUvT7iA7746a3dy6hIo6Z9wp52Vs0cDE1_Hj9IjbpH1uRrnrG8ZIahJDUHeSyOq5pb34dr36zLUHN7byF1ITp4CuUle9D2rHA1Cwfw0XM099lB4dBKUA4IfJ_5wcl6yBJorcX4-y3IaGl0iro8zmeels5O51NgRV90eG8guanzOAZhpfxXPuS2e4jFM123NDbSiCGaRhUARzPQ-MKFscCfq6rM-zivgebme8N-M0KsVdTMjKXX6sbfPnjrKLFpuPaIpWR6kvxpd_hCz_9Zff_5UQqnGgkZig46G7oBTPUK0uirjHD4JcnnqXNPvzTH7JfSiY5tWyTKUHJ4p-465zK2S-ygcJj2pvj6Bcq93XI49dBHK1KDVw4HdVZywcl2QFerbs5wt2-B56UzDj47ieMRFMuN71NnRd90_mqp_Kl0sMosIDhX-2d5dYjJN5Wzdn7UByjYiFXNRnobfYvM8s7W4WJLd70rzO6tfQEx84Znl95CzmtbYE1cdrpjLvMleDcD6-261_cufTqNC_qbtbx7lQlm0cASxkN5G77OBP2N0esijvU0bkgh73cKM79L6x9fzMxt2ilNWnR5YSm0Zf5yyeEqf1y6qfUzCUn6V3p4vlAO6hvKkAbDdRN9Q4r0ih4n7gj9eyRBaK33wz2zCyJYkkNGJ1VpTB-zOSght6_89YhoK7Df-228NUBPuV1x_j2ShuGUgVfGj_6VuYoO9QDYZGSH9zbiy2fkskP4_MskldBGzqpfa42fvvFia7yiPL2JYuS717JlP7qMR3HQMTe_l8fmFMBdjgx5FzYASXUIUKyigzE17IdoJ3WK-7UPpxVSjUvqEShGnLO7Y6BwL3j0iKMqeNQ0IHx2SAa627y7c5WB4RRIEYbEfNUxCU5wSBEp48_5_qfG7K2-grK1QCQTkcWNrFpmi9x-fyUmPScytMAi7jTQdi85Mg9Jdh59MbYfB2ecCZrADHCec0GO_kaX7eKG8rAlRmEsdQq-vYboWdBDTC9TYQuX_rHoKHMo8zYGJyp8W7wosDFMTnkZdzkxWs9j3cmXx41y2fMJgPPKU62jwH41bAdgpPJAt7GAKxMVjssr3iqNlHLwoiA4I3Y-geDr_pQ0J_n1QMe2XXs_NpAP45WHlIxHNtd1xMcxhd9sZAcx9exLLaP7AH5_j-zTnwZNIdImDR3ycKhvMqe68Qvpqbtd9Kf_sQgBMB59fnjdgOFSAdcCRnXfMUqPM0gQpaoDNvBtDe-kskp29sdrnlkEQaqa6Q4dNLktKfTgtD9HYCK8XX0qf3IKxjoR_34zHwdkGc5QhYe7H7VISPFOH2trRnA4pYep631BPj-ErxGUQYUjHWzMGPJybqd4ILS3CaPlsx6yZ_86CoF4VftzvZZAKBtIXogNvR02TkUyhxupYg12tWzObiYySDdyRytYn4sB4dxihJFyOOGh-uV7dIhjbLIVNS--8k8KMZc8NH_chOMSi1lERrFe_0_Ps8DY5aaOtzJrzyYr-gK4OsltFVfDhOKeYUFYNfin6nQuNT7Mq-tzlnYuvXKDgnqZ8nE_kUZu34-aD0j6EHCDRDsCFWHtwbM9JIdkqfUL87ZDY9nciw8qG27M2Lp4JeH8brS2wO1o9hh5qTY2zU54GPK4dxyGah0Dn8HHNlNxTEY2gdvlrAT9Nu1J6en_DTB_zGBUEQuLZJkvRlXy9u_peyHw-AlgLDCWfuZ3e8CP8hS6Ojafw6eaB5yETLHfeUvJeU8Y5WJBvfoujq_muoI6vUQo1xDGBCGZZAXWfvIrJ3InubzEo-R8k_WgOvuAyXIQM74xEMvmFYzWTofxk3DHD_rOl2Jvj362rYhsYzKNPfKA5pVQy8-m0-EDn7R4Y67ybzj3Q-BmPp_8L_C4AouxlDJ4-dZEbhMH0IxNuFcyRIT9x58k4wtx-CbOoCe-CXd-SuVcmU8M6dZnxd1ycCfiNac-9oGrLfJTtW62fQTNudb1sbVUBycTh9rGwLwZfguGs4CSbS3OsXOrC-Xndoe2_MniE9ZDBquTpoqZNfDhobIgPvoOISU7FDRgN3LMi72Rt3H42YBmH09VD01wHrDBwDFHXqMqwXr-qgXspTJNv3IK41RfiY0lla7BGD55oqh1YrGwQK1tuhV8ZL27xIE2lDR4fVEIYdyJXQ-Le5a2gEcyCBkkKou1MGPH527ygXL6CSaX2ooAZ1EgBFl9M6Luc6gztkuqYz3UPK98fkcLtRz99jLdTOlSS9UKDPMX9sPKfEoYpK-LuXNmziCtvAB2vctmkdyKT2tZK01etLAiZvTjfLwApyD8FfbiejFLzbdQdb--XcDqksmRgU1wUHgGjPTG1m2tDDh_YkTra_MJ93pH49_ajsHhHuoLEfvyI-I_rnD3i-Xs-pS04Pi5TwB6mHP-ulXAJl9JHshHO1VzCIJ8jx7k6ssx9CUM7-x0Cbf3zqUUXgyIoRSsxhezc6UiuO2yvgypoPaedmA9tYLCclS-cjYRz-lfTJ1HCLHW-QFE_cyf6G-Fc_7qw2WutU03MwmjGZiPQe9Rp82Vcv5pZvjpuXCAaKF8GvXqsDLDyjoWcfB5nYzpUsnegAB-WbNMjjJEEiegTr-y7IQn7HuOcnbOrBTaCkAs3-FB1HxwaykzYTP1wCxmMh805Hn1wED21_z7spJDo9iJkA3H_ty4TkTxAdNtboz2_2JB4aO9QrL_wKwWlMxJ5lOvxRywOSFucapwPYtqoTMVMi72sYtHuVnzu7ofDuuUyx4FzL3RvYtFOkwXYu6N8TRijy-sd8i7MwbrXdqCwKMX4sPQO7EhK_LlsfBLaO29lDamdzLIQf_c_Dq4EUur2kCfjUy7l7OMxP3Mn2viyfEzbMCt4z3Af7uDpA",
            "release_date": "11 июля 2016",
            "description": "Шигэо Кагэяма вроде бы обычный японский школьник — стеснительный, старающийся не привлекать внимания, не блещущий умом, красотой или чувством юмора. И самое большое его желание — привлечь внимание любимой девушки. Но! У этого восьмиклассника есть экстрасенсорные способности. С детства он взглядом гнет ложки и передвигает предметы. И пусть общественность пока этого не оценила, зато выгоду в этом очень скоро нашел его «ментальный наставник», эксплуатирующий способности Кагэямы себе на поживу.Как будет искать свой путь в этом привычно жестоком мире юный экстрасенс — нам и предстоит увидеть.",
            "opinion": "ABSOLUTE CINEMA",
        },
        {
            "title": "Невероятные приключения ДжоДжо",
            "poster": "https://kinopoisk-ru.clstorage.net/Q152b2H31/3be82betF/9vzxE-f2-w8mL8r8TpKzfXuf9_OYwY-lxyoTkWieGdARYAxyOXsIKFsV-GNXpZ5uozVrNmope6at-uRtTbTOYMf0-AK2irN_C3qynDKD7jQmssvS7fXqhIo6Z9wp52Vs0cDE1_Hj9IjbpH1uRrnrG8ZIahJDUHeSyOq5pb34dr36zLUHN7byF1ITp4CuUle9D2rHA1Cwfw0XM099lB4dBKUA4IfJ_5wcl6yBJorcX4-y3IaGl0iro8zmeels5O51NgRV90eG8guanzOAZhpfxXPuS2e4jFM123NDbSiCGaRhUARzPQ-MKFscCfq6rM-zivgebme8N-M0KsVdTMjKXX6sbfPnjrKLFpuPaIpWR6kvxpd_hCz_9Zff_5UQqnGgkZig46G7oBTPUK0uirjHD4JcnnqXNPvzTH7JfSiY5tWyTKUHJ4p-465zK2S-ygcJj2pvj6Bcq93XI49dBHK1KDVw4HdVZywcl2QFerbs5wt2-B56UzDj47ieMRFMuN71NnRd90_mqp_Kl0sMosIDhX-2d5dYjJN5Wzdn7UByjYiFXNRnobfYvM8s7W4WJLd70rzO6tfQEx84Znl95CzmtbYE1cdrpjLvMleDcD6-261_cufTqNC_qbtbx7lQlm0cASxkN5G77OBP2N0esijvU0bkgh73cKM79L6x9fzMxt2ilNWnR5YSm0Zf5yyeEqf1y6qfUzCUn6V3p4vlAO6hvKkAbDdRN9Q4r0ih4n7gj9eyRBaK33wz2zCyJYkkNGJ1VpTB-zOSght6_89YhoK7Df-228NUBPuV1x_j2ShuGUgVfGj_6VuYoO9QDYZGSH9zbiy2fkskP4_MskldBGzqpfa42fvvFia7yiPL2JYuS717JlP7qMR3HQMTe_l8fmFMBdjgx5FzYASXUIUKyigzE17IdoJ3WK-7UPpxVSjUvqEShGnLO7Y6BwL3j0iKMqeNQ0IHx2SAa627y7c5WB4RRIEYbEfNUxCU5wSBEp48_5_qfG7K2-grK1QCQTkcWNrFpmi9x-fyUmPScytMAi7jTQdi85Mg9Jdh59MbYfB2ecCZrADHCec0GO_kaX7eKG8rAlRmEsdQq-vYboWdBDTC9TYQuX_rHoKHMo8zYGJyp8W7wosDFMTnkZdzkxWs9j3cmXx41y2fMJgPPKU62jwH41bAdgpPJAt7GAKxMVjssr3iqNlHLwoiA4I3Y-geDr_pQ0J_n1QMe2XXs_NpAP45WHlIxHNtd1xMcxhd9sZAcx9exLLaP7AH5_j-zTnwZNIdImDR3ycKhvMqe68Qvpqbtd9Kf_sQgBMB59fnjdgOFSAdcCRnXfMUqPM0gQpaoDNvBtDe-kskp29sdrnlkEQaqa6Q4dNLktKfTgtD9HYCK8XX0qf3IKxjoR_34zHwdkGc5QhYe7H7VISPFOH2trRnA4pYep631BPj-ErxGUQYUjHWzMGPJybqd4ILS3CaPlsx6yZ_86CoF4VftzvZZAKBtIXogNvR02TkUyhxupYg12tWzObiYySDdyRytYn4sB4dxihJFyOOGh-uV7dIhjbLIVNS--8k8KMZc8NH_chOMSi1lERrFe_0_Ps8DY5aaOtzJrzyYr-gK4OsltFVfDhOKeYUFYNfin6nQuNT7Mq-tzlnYuvXKDgnqZ8nE_kUZu34-aD0j6EHCDRDsCFWHtwbM9JIdkqfUL87ZDY9nciw8qG27M2Lp4JeH8brS2wO1o9hh5qTY2zU54GPK4dxyGah0Dn8HHNlNxTEY2gdvlrAT9Nu1J6en_DTB_zGBUEQuLZJkvRlXy9u_peyHw-AlgLDCWfuZ3e8CP8hS6Ojafw6eaB5yETLHfeUvJeU8Y5WJBvfoujq_muoI6vUQo1xDGBCGZZAXWfvIrJ3InubzEo-R8k_WgOvuAyXIQM74xEMvmFYzWTofxk3DHD_rOl2Jvj362rYhsYzKNPfKA5pVQy8-m0-EDn7R4Y67ybzj3Q-BmPp_8L_C4AouxlDJ4-dZEbhMH0IxNuFcyRIT9x58k4wtx-CbOoCe-CXd-SuVcmU8M6dZnxd1ycCfiNac-9oGrLfJTtW62fQTNudb1sbVUBycTh9rGwLwZfguGs4CSbS3OsXOrC-Xndoe2_MniE9ZDBquTpoqZNfDhobIgPvoOISU7FDRgN3LMi72Rt3H42YBmH09VD01wHrDBwDFHXqMqwXr-qgXspTJNv3IK41RfiY0lla7BGD55oqh1YrGwQK1tuhV8ZL27xIE2lDR4fVEIYdyJXQ-Le5a2gEcyCBkkKou1MGPH527ygXL6CSaX2ooAZ1EgBFl9M6Luc6gztkuqYz3UPK98fkcLtRz99jLdTOlSS9UKDPMX9sPKfEoYpK-LuXNmziCtvAB2vctmkdyKT2tZK01etLAiZvTjfLwApyD8FfbiejFLzbdQdb--XcDqksmRgU1wUHgGjPTG1m2tDDh_YkTra_MJ93pH49_ajsHhHuoLEfvyI-I_rnD3i-Xs-pS04Pi5TwB6mHP-ulXAJl9JHshHO1VzCIJ8jx7k6ssx9CUM7-x0Cbf3zqUUXgyIoRSsxhezc6UiuO2yvgypoPaedmA9tYLCclS-cjYRz-lfTJ1HCLHW-QFE_cyf6G-Fc_7qw2WutU03MwmjGZiPQe9Rp82Vcv5pZvjpuXCAaKF8GvXqsDLDyjoWcfB5nYzpUsnegAB-WbNMjjJEEiegTr-y7IQn7HuOcnbOrBTaCkAs3-FB1HxwaykzYTP1wCxmMh805Hn1wED21_z7spJDo9iJkA3H_ty4TkTxAdNtboz2_2JB4aO9QrL_wKwWlMxJ5lOvxRywOSFucapwPYtqoTMVMi72sYtHuVnzu7ofDuuUyx4FzL3RvYtFOkwXYu6N8TRijy-sd8i7MwbrXdqCwKMX4sPQO7EhK_LlsfBLaO29lDamdzLIQf_c_Dq4EUur2kCfjUy7l7OMxP3Mn2viyfEzbMCt4z3Af7uDpA",
            "release_date": "4 октября 2012",
            "description": "История девяти частей манги разворачивается вокруг приключений Джонатана Джостара и его потомков: каждая часть представляет читателю отдельную историю и нового героя, способного применять в бою сверхъестественные способности.",
            "opinion": "ABSOLUTE CINEMA",
        },
        {
            "title": "Опасность в моём сердце",
            "poster": "https://kinopoisk-ru.clstorage.net/Q152b2H31/3be82betF/9vzxE-f2-w8mL8r8TpKzfXuf9_OYwY-lxyoTkWieGdARYAxyOXsIKFsV-GNLhYpmtyFrFm9hZvqou6htVPWfHMf1kCK6i9N-S3KyiD_WmiQ2st6u6cSqhIo6Z9wp52Vs0cDE1_Hj9IjbpH1uRrnrG8ZIahJDUHeSyOq5pb34dr36zLUHN7byF1ITp4CuUle9D2rHA1Cwfw0XM099lB4dBKUA4IfJ_5wcl6yBJorcX4-y3IaGl0iro8zmeels5O51NgRV90eG8guanzOAZhpfxXPuS2e4jFM123NDbSiCGaRhUARzPQ-MKFscCfq6rM-zivgebme8N-M0KsVdTMjKXX6sbfPnjrKLFpuPaIpWR6kvxpd_hCz_9Zff_5UQqnGgkZig46G7oBTPUK0uirjHD4JcnnqXNPvzTH7JfSiY5tWyTKUHJ4p-465zK2S-ygcJj2pvj6Bcq93XI49dBHK1KDVw4HdVZywcl2QFerbs5wt2-B56UzDj47ieMRFMuN71NnRd90_mqp_Kl0sMosIDhX-2d5dYjJN5Wzdn7UByjYiFXNRnobfYvM8s7W4WJLd70rzO6tfQEx84Znl95CzmtbYE1cdrpjLvMleDcD6-261_cufTqNC_qbtbx7lQlm0cASxkN5G77OBP2N0esijvU0bkgh73cKM79L6x9fzMxt2ilNWnR5YSm0Zf5yyeEqf1y6qfUzCUn6V3p4vlAO6hvKkAbDdRN9Q4r0ih4n7gj9eyRBaK33wz2zCyJYkkNGJ1VpTB-zOSght6_89YhoK7Df-228NUBPuV1x_j2ShuGUgVfGj_6VuYoO9QDYZGSH9zbiy2fkskP4_MskldBGzqpfa42fvvFia7yiPL2JYuS717JlP7qMR3HQMTe_l8fmFMBdjgx5FzYASXUIUKyigzE17IdoJ3WK-7UPpxVSjUvqEShGnLO7Y6BwL3j0iKMqeNQ0IHx2SAa627y7c5WB4RRIEYbEfNUxCU5wSBEp48_5_qfG7K2-grK1QCQTkcWNrFpmi9x-fyUmPScytMAi7jTQdi85Mg9Jdh59MbYfB2ecCZrADHCec0GO_kaX7eKG8rAlRmEsdQq-vYboWdBDTC9TYQuX_rHoKHMo8zYGJyp8W7wosDFMTnkZdzkxWs9j3cmXx41y2fMJgPPKU62jwH41bAdgpPJAt7GAKxMVjssr3iqNlHLwoiA4I3Y-geDr_pQ0J_n1QMe2XXs_NpAP45WHlIxHNtd1xMcxhd9sZAcx9exLLaP7AH5_j-zTnwZNIdImDR3ycKhvMqe68Qvpqbtd9Kf_sQgBMB59fnjdgOFSAdcCRnXfMUqPM0gQpaoDNvBtDe-kskp29sdrnlkEQaqa6Q4dNLktKfTgtD9HYCK8XX0qf3IKxjoR_34zHwdkGc5QhYe7H7VISPFOH2trRnA4pYep631BPj-ErxGUQYUjHWzMGPJybqd4ILS3CaPlsx6yZ_86CoF4VftzvZZAKBtIXogNvR02TkUyhxupYg12tWzObiYySDdyRytYn4sB4dxihJFyOOGh-uV7dIhjbLIVNS--8k8KMZc8NH_chOMSi1lERrFe_0_Ps8DY5aaOtzJrzyYr-gK4OsltFVfDhOKeYUFYNfin6nQuNT7Mq-tzlnYuvXKDgnqZ8nE_kUZu34-aD0j6EHCDRDsCFWHtwbM9JIdkqfUL87ZDY9nciw8qG27M2Lp4JeH8brS2wO1o9hh5qTY2zU54GPK4dxyGah0Dn8HHNlNxTEY2gdvlrAT9Nu1J6en_DTB_zGBUEQuLZJkvRlXy9u_peyHw-AlgLDCWfuZ3e8CP8hS6Ojafw6eaB5yETLHfeUvJeU8Y5WJBvfoujq_muoI6vUQo1xDGBCGZZAXWfvIrJ3InubzEo-R8k_WgOvuAyXIQM74xEMvmFYzWTofxk3DHD_rOl2Jvj362rYhsYzKNPfKA5pVQy8-m0-EDn7R4Y67ybzj3Q-BmPp_8L_C4AouxlDJ4-dZEbhMH0IxNuFcyRIT9x58k4wtx-CbOoCe-CXd-SuVcmU8M6dZnxd1ycCfiNac-9oGrLfJTtW62fQTNudb1sbVUBycTh9rGwLwZfguGs4CSbS3OsXOrC-Xndoe2_MniE9ZDBquTpoqZNfDhobIgPvoOISU7FDRgN3LMi72Rt3H42YBmH09VD01wHrDBwDFHXqMqwXr-qgXspTJNv3IK41RfiY0lla7BGD55oqh1YrGwQK1tuhV8ZL27xIE2lDR4fVEIYdyJXQ-Le5a2gEcyCBkkKou1MGPH527ygXL6CSaX2ooAZ1EgBFl9M6Luc6gztkuqYz3UPK98fkcLtRz99jLdTOlSS9UKDPMX9sPKfEoYpK-LuXNmziCtvAB2vctmkdyKT2tZK01etLAiZvTjfLwApyD8FfbiejFLzbdQdb--XcDqksmRgU1wUHgGjPTG1m2tDDh_YkTra_MJ93pH49_ajsHhHuoLEfvyI-I_rnD3i-Xs-pS04Pi5TwB6mHP-ulXAJl9JHshHO1VzCIJ8jx7k6ssx9CUM7-x0Cbf3zqUUXgyIoRSsxhezc6UiuO2yvgypoPaedmA9tYLCclS-cjYRz-lfTJ1HCLHW-QFE_cyf6G-Fc_7qw2WutU03MwmjGZiPQe9Rp82Vcv5pZvjpuXCAaKF8GvXqsDLDyjoWcfB5nYzpUsnegAB-WbNMjjJEEiegTr-y7IQn7HuOcnbOrBTaCkAs3-FB1HxwaykzYTP1wCxmMh805Hn1wED21_z7spJDo9iJkA3H_ty4TkTxAdNtboz2_2JB4aO9QrL_wKwWlMxJ5lOvxRywOSFucapwPYtqoTMVMi72sYtHuVnzu7ofDuuUyx4FzL3RvYtFOkwXYu6N8TRijy-sd8i7MwbrXdqCwKMX4sPQO7EhK_LlsfBLaO29lDamdzLIQf_c_Dq4EUur2kCfjUy7l7OMxP3Mn2viyfEzbMCt4z3Af7uDpA",
            "release_date": "9 ноября 2022",
            "description": "У тихого и замкнутого школьника Кётаро Итикавы весьма богатое воображение, ведь он постоянно представляет, как убивает одноклассников различными способами, и особенно часто — самую красивую девочку класса Анну Ямаду. Однажды он случайно сталкивается с Анной в библиотеке, и с удивлением отмечает, что она очень милая и забавная. Постепенно Кётаро начинает испытывать к девушке новые для себя чувства.",
            "opinion": "ABSOLUTE CINEMA",
        },
    ]

    page.bgcolor = ft.colors.TRANSPARENT
    page.bg_gradient = ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=[
            ft.Colors.BLUE_GREY_900,
            ft.Colors.WHITE,
            ft.Colors.BLUE_400,
        ],
    )

    def create_anime_card(anime):
        print(f"Попытка загрузить изображение: {anime['poster']}")
        poster = ft.Image(
            src=anime["poster"],
            width=200,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Text("Изображение не загрузилось", color=ft.colors.RED),
        )
        title = ft.Text(
            anime["title"],
            size=18,
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.WHITE,
        )
        button = ft.ElevatedButton(
            "Подробнее",
            on_click=lambda _: page.go(f"/details/{anime_list.index(anime)}"),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_700,
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        card = ft.Container(
            content=ft.Column(
                [poster, title, button],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=250,
            height=500,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.colors.GREY_700, ft.colors.GREY_800],
            ),
            border_radius=10,
            padding=10,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=10,
                color=ft.colors.BLACK54,
                offset=ft.Offset(0, 4),
            ),
        )
        return card

    cards = [create_anime_card(anime) for anime in anime_list]

    top_row = ft.Row(cards[:3], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    bottom_row = ft.Row(cards[3:], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    gallery_title = ft.Text(
        "Галерея аниме", size=24, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE
    )
    back_button = ft.ElevatedButton(
        "Назад",
        on_click=lambda _: page.go("/"),
        style=ft.ButtonStyle(
            bgcolor=ft.colors.BLUE_700,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    gallery_content = ft.Column(
        [gallery_title, back_button, top_row, bottom_row],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
    )

    gallery_container = ft.Container(
        content=gallery_content, alignment=ft.alignment.center, expand=True
    )

    welcome_text = ft.Text(
        "Добро пожаловать в виртуальный музей моих любимых аниме!",
        size=24,
        text_align=ft.TextAlign.CENTER,
        color=ft.colors.WHITE,
    )
    welcome_button = ft.ElevatedButton(
        "Перейти в галерею",
        on_click=lambda _: page.go("/gallery"),
        style=ft.ButtonStyle(
            bgcolor=ft.colors.BLUE_700,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    welcome_container = ft.Container(
        content=ft.Column(
            [welcome_text, welcome_button],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )

    def create_details_page(anime):
        poster = ft.Image(
            src=anime["poster"], width=400, height=400, fit=ft.ImageFit.CONTAIN
        )
        title = ft.Text(
            anime["title"],
            size=28,
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.WHITE,
        )
        release_date = ft.Text(
            f"Дата выхода: {anime['release_date']}",
            size=18,
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.WHITE,
        )

        description_block = ft.Container(
            content=ft.Text(
                anime["description"],
                size=16,
                text_align=ft.TextAlign.JUSTIFY,
                color=ft.colors.WHITE,
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.colors.GREY_700, ft.colors.GREY_800],
            ),
            padding=20,
            border_radius=10,
            width=600,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=10,
                color=ft.colors.BLACK54,
                offset=ft.Offset(0, 4),
            ),
        )

        opinion_block = ft.Container(
            content=ft.Text(
                anime["opinion"],
                size=16,
                text_align=ft.TextAlign.JUSTIFY,
                color=ft.colors.WHITE,
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.colors.GREY_700, ft.colors.GREY_800],
            ),
            padding=20,
            border_radius=10,
            width=600,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=10,
                color=ft.colors.BLACK54,
                offset=ft.Offset(0, 4),
            ),
        )

        back_button = ft.ElevatedButton(
            "Назад",
            on_click=lambda _: page.go("/gallery"),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_700,
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        details_content = ft.Column(
            [
                poster,
                title,
                release_date,
                description_block,
                opinion_block,
                back_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

        return ft.Container(
            content=details_content, alignment=ft.alignment.center, expand=True
        )

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [welcome_container],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    bgcolor=ft.colors.TRANSPARENT,
                )
            )
        elif page.route == "/gallery":
            page.views.append(
                ft.View(
                    "/gallery",
                    [gallery_container],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    bgcolor=ft.colors.TRANSPARENT,
                )
            )
        elif page.route.startswith("/details/"):
            try:
                index = int(page.route.split("/")[-1])
                if 0 <= index < len(anime_list):
                    details_container = create_details_page(anime_list[index])
                    page.views.append(
                        ft.View(
                            f"/details/{index}",
                            [details_container],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            vertical_alignment=ft.MainAxisAlignment.CENTER,
                            bgcolor=ft.colors.TRANSPARENT,
                        )
                    )
                else:
                    page.go("/gallery")
            except ValueError:
                page.go("/gallery")
        page.update()

    page.on_route_change = route_change
    page.go("/")


ft.app(
    target=main,
)
