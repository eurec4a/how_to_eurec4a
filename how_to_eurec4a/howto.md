# How-To

## How-To add new datasets

The [EUREC$^4$A-Intake catalog](https://github.com/eurec4a/eurec4a-intake) is the dataset collection of the EUREC$^4$A and ATOMIC field campaign. It is a collection of `yaml`-files that contain references to the dataset storage locations.

Datasets should be added by following these steps:

### via the command line
1. Cloning the [EUREC$^4$A-Intake catalog](https://github.com/eurec4a/eurec4a-intake) repository with
   ```bash
   git clone git@github.com:eurec4a/eurec4a-intake.git
   ```
2. Create a new branch
   ```bash
   git checkout -b <my_new_dataset>
   ```
3. Add new catalog entry
   The catalog contains two types of entries:
   - references to sub-catalogs
   - references to a dataset

   The surface flux dataset from the research vessel Meteor is accessible via
   ```python
   cat.Meteor.surface_fluxes
   ```
   and is saved in the file [Meteor/main.yaml](https://github.com/eurec4a/eurec4a-intake/blob/master/Meteor/main.yaml).
   The radar dataset, which is more complex and contains several subsets is accessible via
   ```python
   cat.Meteor.LIMRAD94.low_res
   cat.Meteor.LIMRAD94.high_res
   ```
   For the creation of the `LIMRAD94` subset, a sub-catalog reference has been created in [Meteor/main.yaml](https://github.com/eurec4a/eurec4a-intake/blob/master/Meteor/main.yaml). The final reference to the dataset is added in [Meteor/LIMRAD94.yaml](https://github.com/eurec4a/eurec4a-intake/blob/master/Meteor/LIMRAD94.yaml)

   Depending on the complexity of the dataset, an entry can be directly added to the `main.yaml` file of the respective platform/simulation 
   ```bash
   vi <platform>/main.yaml
   ```
   
   or to a (new) instrument specific file

   ```
   vi <platform>/<instrument>.yaml
   ```

   The reference has the following format:
   ```yaml
   plugins:
      source:
       - module: intake_xarray

   sources:
     <dataset_name>:
       description: <short description of the dataset>
       driver: opendap
       args:
         auth: null
         urlpath: <url_to_dataset>
         chunks: {}
         engine: netcdf4
   ```

   In case your dataset has been published on AERIS, the THREDDS link to your dataset can be determined by finding your dataset at [https://observations.ipsl.fr/aeris/eurec4a-data/](https://observations.ipsl.fr/aeris/eurec4a-data/) and then replace in the link to the dataset `https://observations.ipsl.fr/aeris/eurec4a-data/` with `https://observations.ipsl.fr/thredds/dodsC/EUREC4A/`. You can check if the link is correct by opening it e.g. directly with `xarray.open_dataset()` or [Panoply](https://www.giss.nasa.gov/tools/panoply/) by opening a `Remote Dataset`. 

   A sub-catalog reference can be created with
   ```yaml
   sources:
     <instrument/model_name>:
       args:
         path: "{{CATALOG_DIR}}/<instrument/model_name>.yaml"
       description: '<Instrument/model description>'
       driver: yaml_file_cat
       metadata: {}
   ```

   Please also check out entries already present in the EUREC$^4$A-Intake catalog.

   Finally those changes need to be staged and committed.
   ```bash
   git add -p
   ```
   ```bash
git commit -m "<Adding my_new_dataset>"
   ```

4. Push branch to GitHub
   ```bash
   git push --set-upstream origin <my_new_dataset>
   ```

5. Create pull request on GitHub
   A pull request can be started on the GitHub webpage. After the pull request has been submitted, the review process will start. To accellerate the process, please make sure all tests for your pull request succeed. The status of the tests are shown at the bottom of your pull request.

### via GitHub web interface 
