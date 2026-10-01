# Release notes

<!-- do not remove -->

## 0.1.1

### New Features

- Update the package metadata and description, and trim the README quick start ([#16](https://github.com/franckalbinet/soilspectfm/issues/16))


## 0.1.0

### Breaking Changes

- Require Python 3.10 or later, and SoilSpecData 0.2 or later ([#6](https://github.com/franckalbinet/soilspectfm/issues/6))
- Ship the toy datasets with the package, and remove `toy_mir_url` and `toy_noisy_mir_url` ([#5](https://github.com/franckalbinet/soilspectfm/issues/5))
- `Resample` raises an error for targets outside the source range ([#4](https://github.com/franckalbinet/soilspectfm/issues/4))
- Remove the `n_jobs` parameter from `MSC` ([#3](https://github.com/franckalbinet/soilspectfm/issues/3))
- Replace `TakeDerivative` and `SavGolSmooth` with `SavitzkyGolay` ([#2](https://github.com/franckalbinet/soilspectfm/issues/2))
- Rename `core` to `preprocessing` and `utils` to `datasets`, and add `soilspectfm.all` ([#1](https://github.com/franckalbinet/soilspectfm/issues/1))

### New Features

- Document every transformer with tested examples, rewrite the README, and align the docs layout with SoilSpecData ([#9](https://github.com/franckalbinet/soilspectfm/issues/9))
- `MSC`, `Resample` and `SavitzkyGolay` process all spectra in one call ([#8](https://github.com/franckalbinet/soilspectfm/issues/8))
- `Resample` accepts decreasing wavenumbers, and checks that `X` matches `source_x` ([#7](https://github.com/franckalbinet/soilspectfm/issues/7))

### Bugs Squashed

- pandas was missing from the package dependencies ([#15](https://github.com/franckalbinet/soilspectfm/issues/15))
- `MSC` rejected an invalid `reference_method` with `assert`, and reported an unfitted instance as fitted ([#14](https://github.com/franckalbinet/soilspectfm/issues/14))
- `plot_spectra` could plot the same spectrum twice ([#13](https://github.com/franckalbinet/soilspectfm/issues/13))
- `Trim` treated a bound of 0 as no bound ([#12](https://github.com/franckalbinet/soilspectfm/issues/12))
- `WaveletDenoise` changed its state in `transform` ([#11](https://github.com/franckalbinet/soilspectfm/issues/11))
- `Resample` ignored `interpolation_kind` ([#10](https://github.com/franckalbinet/soilspectfm/issues/10))
