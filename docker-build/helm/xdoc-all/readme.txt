Thou!!!!
Please, read carefully to avoid mistake.
Thou will pay extremely cost if thou just glance this.
-------------------------------------------------------
In this directory thou just care about bellow list, no more..
------------------------------------------------------
data
├── aws.yml                             # AWS deployment-value
├── lacviet.yml                         # Lac Viet deployment-value
├── dev.yml                             # Dev and QC deployment-value
├── jobs.app.yml                        # List of File-Job values
└── job.cron.yml                        # List of Cron-Job values, all Cron Job POD run one time
templates
├── web.apps.yml                        # Web API pod deployment
├── web.config.yml                      # All config for Web API
├── web.namespace.yml                   # Namespace for Web API, wrong namespace will make chain of error,  through and through all PODs
├── web.service.yml                     # Make a service link to web app. The service allow another POD can access to Web Api app
├── jobs.config.yml                     # All configuration infor serve for JOB and cron job
├── jobs.apps.yml                       # All apps in which File-Processing run
├── jobs.cron.yml                       # All dataset deployment
├── jobs.namespace.yml                  # Namespace for Job and cron job deploy
├── long.horn.namespace.yml             # Longhorn namespace.Till now, Longhorn is unofficially volume (pilot test)
└── long.horn.yml                       # Longhorn claim