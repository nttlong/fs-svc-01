"""
This library provide a service in which stats all information about sizes and number of items in an application
Stats of File-Service including:
    Total of:
        1 - Finished items
        2 - Unfinished items (an unfinished item in case.A
            file was still uploading. Remember that: Some big file spend several days to finish content)
    Service also stat each day in a whole time of File-Service-System

    The stat looks like:

        total_items:...
        total_unfinished_items: ...
        total_size: ...
        total_unfinished_size: ...
        total_real_size: ...
        └── 2023
            ├── total_items:...
            ├── total_unfinished_items: ...
            ├── total_size: ...
            ├── total_unfinished_size: ...
            ├── total_real_size: ...
            ├── 01:
            │   ├── 01:
            │   │   ├── total_items:...
            │   │   ├── total_unfinished_items: ...
            │   │   ├── total_size: ...
            │   │   ├── total_unfinished_size: ...
            │   │   └── total_real_size: ...
            │   ├── ...
            │   ├── 30:
            │   │   ├── total_items:...
            │   │   ├── total_unfinished_items: ...
            │   │   ├── total_size: ...
            │   │   ├── total_unfinished_size: ...
            │   │   └── total_real_size: ...
            │   ├── total_items:...
            │   ├── total_unfinished_items: ...
            │   ├── total_size: ...
            │   ├── total_unfinished_size: ...
            │   └── total_real_size: ...
            ├── ...
            └── 12
                ├──
                │   ├── total_items:...
                │   ├── total_unfinished_items: ...
                │   ├── total_size: ...
                │   ├── total_unfinished_size: ...
                │   ├── total_real_size: ...
                │   └── total_items:...
                ├── total_unfinished_items: ...
                ├── total_size: ...
                ├── total_unfinished_size: ...
                └── total_real_size: ...
        ...
        └── 2024

"""
import datetime

import cy_docs
import cy_kit
from cyx.base import DbConnect

"""
Need a db connection to do everything else
"""
import cy_xdoc

"""
Very useful lib for Mongodb manipulation
"""

from cy_xdoc.models.apps import App
from cy_xdoc.models.files import DocUploadRegister
from cyx.models import FsFile


class AppStatServices:
    """
    All about stat of application here
    """

    def __init__(self, db_connect: DbConnect = cy_kit.singleton(DbConnect)):
        self.db_connect = db_connect

    def quick_stats(self, app_name: str, from_year: int, to_year: int):
        t= datetime.datetime.now()
        unit = 1024 * 1024
        docs = self.db_connect.db(app_name).doc(DocUploadRegister)
        total_items = cy_docs.fields.total_items >> cy_docs.FUNCS.sum(
            cy_docs.FUNCS.cond((
                    (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                    (docs.fields.Status == 1)
            ), 1, 0)
        )
        total_size = cy_docs.fields.total_items >> cy_docs.FUNCS.sum(
            cy_docs.FUNCS.cond(
                (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                (docs.fields.Status == 1)
                , docs.fields.SizeInBytes / unit, 0)
        )
        total_unfinished_items = cy_docs.fields.total_unfinished_items >> cy_docs.FUNCS.sum(
            cy_docs.FUNCS.cond(
                (docs.fields.SizeInBytes < docs.fields.SizeUploaded)
                , 1, 0)
        )
        total_unfinished_size = cy_docs.fields.total_unfinished_items >> cy_docs.FUNCS.sum(
            cy_docs.FUNCS.cond(
                (docs.fields.SizeInBytes < docs.fields.SizeUploaded)
                , docs.fields.SizeInBytes / unit, 0)
        )
        selector = [
            total_items,
            total_unfinished_items,
            total_size,
            total_unfinished_size
        ]
        for year in range(from_year, to_year + 1):
            year_str = "{:04d}".format(year)
            total_items_year = cy_docs.fields[f"total_items_{year_str}"] >> \
                               cy_docs.FUNCS.sum(
                                   cy_docs.FUNCS.cond((
                                           (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                           (docs.fields.Status == 1) &
                                           (docs.fields.RegisterOn.year() == year)
                                   ), 1, 0)
                               )
            total_unfinished_items_year = cy_docs.fields[f"total_unfinished_items_{year_str}"] >> \
                                          cy_docs.FUNCS.sum(
                                              cy_docs.FUNCS.cond((
                                                      (docs.fields.SizeInBytes < docs.fields.SizeUploaded) & \
                                                      (docs.fields.RegisterOn.year() == year)
                                              ), 1, 0)
                                          )

            total_size_year = cy_docs.fields[f"total_size_{year_str}"] >> \
                              cy_docs.FUNCS.sum(
                                  cy_docs.FUNCS.cond((
                                          (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                          (docs.fields.Status == 1) &
                                          (docs.fields.RegisterOn.year() == year)
                                  ), docs.fields.SizeInBytes, 0)
                              )
            total_unfinished_size_year = cy_docs.fields[f"total_unfinished_size_{year_str}"] >> \
                                         cy_docs.FUNCS.sum(
                                             cy_docs.FUNCS.cond((
                                                     (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                     (docs.fields.Status == 1) &
                                                     (docs.fields.RegisterOn.year() == year)
                                             ), docs.fields.SizeInBytes, 0)
                                         )
            selector += [
                total_items_year,
                total_unfinished_items_year,
                total_size_year,
                total_unfinished_size_year
            ]
            for montth in range(1, 13):
                montth_str = "{:02d}".format(montth)
                total_items_month = cy_docs.fields[f"total_items_{year_str}_{montth_str}"] >> \
                                    cy_docs.FUNCS.sum(
                                        cy_docs.FUNCS.cond((
                                                (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                (docs.fields.Status == 1) &
                                                (docs.fields.RegisterOn.year() == year) & \
                                                (docs.fields.RegisterOn.month() == montth)
                                        ), 1, 0)
                                    )
                total_unfinished_items_month = cy_docs.fields[f"total_unfinished_items_{year_str}_{montth_str}"] >> \
                                               cy_docs.FUNCS.sum(
                                                   cy_docs.FUNCS.cond((
                                                           (docs.fields.SizeInBytes < docs.fields.SizeUploaded) & \
                                                           (docs.fields.RegisterOn.year() == year) & \
                                                           (docs.fields.RegisterOn.month() == montth)
                                                   ), 1, 0)
                                               )

                total_size_month = cy_docs.fields[f"total_size_{year_str}_{montth_str}"] >> \
                                   cy_docs.FUNCS.sum(
                                       cy_docs.FUNCS.cond((
                                               (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                               (docs.fields.Status == 1) &
                                               (docs.fields.RegisterOn.year() == year) & \
                                               (docs.fields.RegisterOn.month() == montth)
                                       ), docs.fields.SizeInBytes, 0)
                                   )
                total_unfinished_size_month = cy_docs.fields[f"total_unfinished_size_{year_str}_{montth_str}"] >> \
                                              cy_docs.FUNCS.sum(
                                                  cy_docs.FUNCS.cond((
                                                          (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                          (docs.fields.Status == 1) &
                                                          (docs.fields.RegisterOn.year() == year) & \
                                                          (docs.fields.RegisterOn.month() == montth)
                                                  ), docs.fields.SizeInBytes, 0)
                                              )

                selector += [
                    total_items_month,
                    total_unfinished_items_month,
                    total_size_month,
                    total_unfinished_size_month
                ]

                for day in range(1, 32):
                    day_str = "{:02d}".format(montth)
                    total_items_day = cy_docs.fields[f"total_items_{year_str}_{montth_str}_{day_str}"] >> \
                                      cy_docs.FUNCS.sum(
                                          cy_docs.FUNCS.cond((
                                                  (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                  (docs.fields.Status == 1) &
                                                  (docs.fields.RegisterOn.year() == year) & \
                                                  (docs.fields.RegisterOn.month() == montth) & \
                                                  (docs.fields.RegisterOn.day() == day)
                                          ), 1, 0)
                                      )
                    total_unfinished_items_day = cy_docs.fields[
                                                     f"total_unfinished_items_{year_str}_{montth_str}_{day_str}"] >> \
                                                 cy_docs.FUNCS.sum(
                                                     cy_docs.FUNCS.cond((
                                                             (docs.fields.SizeInBytes < docs.fields.SizeUploaded) & \
                                                             (docs.fields.RegisterOn.year() == year) & \
                                                             (docs.fields.RegisterOn.month() == montth) & \
                                                             (docs.fields.RegisterOn.day() == day)
                                                     ), 1, 0)
                                                 )

                    total_size_day = cy_docs.fields[f"total_size_{year_str}_{montth_str}"] >> \
                                     cy_docs.FUNCS.sum(
                                         cy_docs.FUNCS.cond((
                                                 (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                 (docs.fields.Status == 1) &
                                                 (docs.fields.RegisterOn.year() == year) & \
                                                 (docs.fields.RegisterOn.month() == montth) & \
                                                 (docs.fields.RegisterOn.day() == day)
                                         ), docs.fields.SizeInBytes, 0)
                                     )
                    total_unfinished_size_day = cy_docs.fields[
                                                    f"total_unfinished_size_{year_str}_{montth_str}_{day_str}"] >> \
                                                cy_docs.FUNCS.sum(
                                                    cy_docs.FUNCS.cond((
                                                            (docs.fields.SizeInBytes == docs.fields.SizeUploaded) & \
                                                            (docs.fields.Status == 1) &
                                                            (docs.fields.RegisterOn.year() == year) & \
                                                            (docs.fields.RegisterOn.month() == montth) & \
                                                            (docs.fields.RegisterOn.day() == day)
                                                    ), docs.fields.SizeInBytes, 0)
                                                )

                    selector += [
                        total_items_day,
                        total_unfinished_items_day,
                        total_size_day,
                        total_unfinished_size_day
                    ]
        n = (datetime.datetime.now() - t).total_seconds()
        print(n)
        agg = docs.context.aggregate().project(
            *tuple(selector)
        )

        # agg.project(
        #     {
        #         "Year":
        #     }
        # )
        ret = agg.first_item()
        return ret
