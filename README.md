This repository and associated code is originaly from:

> Visconti di Oleggio Castello, M., Chauhan,  V., Jiahui, G., & Gobbini, M. I. (2020).  *mvdoc/budapest-fmri-data*. Zenodo.  http://doi.org/10.5281/zenodo.3942173

It has since been edited by me (@aim) for comparison with Marvi et al (2025). I only used this code to present the stimuli in the scanner, *NOT* to process any resulting data (as of 06/2025).

## Cloning this repository and downloading the dataset

To clone this repository, run

```bash
$ git clone https://github.com/aimarvi/budapest.git
```

## Setting up a python environment
```bash
$ conda env create -f conda-environment.yml --name budapest
$ conda activate budapest
$ pip install ./code
```

See [Presentation scripts](#presentation-scripts)

## Presentation, preprocessing, and quality assurance scripts

In this repository the original authors provided the scripts used to generate and preprocess the stimuli, to present the stimuli in the scanner, to preprocess the fMRI data, and to run quality assurance analyses. These scripts can be found in the [`scripts`](scripts) directory. In particular,

- [`scripts/preprocessing-stimulus`](scripts/preprocessing-stimulus) contains the scripts to
  split the movie into separate parts to be presented in the scanner, and preprocess the audio of the movie to make it more audible in the scanner.
- [`scripts/presentation`](scripts/presentation) contains PsychoPy presentation scripts.
- [`scripts/preprocessing-fmri`](scripts/preprocessing-fmri) contains the scripts used to run [fMRIprep](https://fmriprep.readthedocs.io/) for preprocessing.
- [`scripts/quality-assurance`](scripts/quality-assurance) contains scripts to run QA analyses and generate the figures reported in the data paper.
- [`scripts/hyperalignment-and-decoding`](hyperalignment-and-decoding) contains scripts to perform hyperalignment and movie segment classification.
- [`notebooks`](notebooks) contains jupyter notebooks to generate figures and run additional analyses.

### Stimuli

The movie was extracted from a DVD and converted into mkv (`libmkv 0.6.5.1`) format using [HandBrake](https://handbrake.fr/). Unfortunately, this process was not scripted. The DVD had [UPC code 024543897385](https://www.upcitemdb.com/upc/24543897385). We provide additional metadata associated with the converted movie file to make sure that future conversions would match our stimuli as best as possible. The information is available in [`scripts/preprocessing-stimulus/movie-file-info.txt`](scripts/preprocessing-stimulus/movie-file-info.txt). The total duration of the movie was `01:39:55.17`. The video and audio were encoded with the following codecs:

```
Stream #0:0(eng): Video: h264 (High), yuv420p(tv, smpte170m/smpte170m/bt709, progressive), 720x480 [SAR 32:27 DAR 16:9], SAR 186:157 DAR 279:157, 30 fps, 30 tbr, 1k tbn, 60 tbc (default)
Stream #0:1(eng): Audio: ac3, 48000 Hz, stereo, fltp, 160 kb/s (default)
Stream #0:2(eng): Audio: ac3, 48000 Hz, 5.1(side), fltp, 384 kb/s
```
I am not including the `.mp4` files here because they're too large. please reach out at amarvi@mit.edu if you'd like them. Our scan was a shortened version of the original localizer, using only runs 2,3 for a total of ~15 minutes of scantime. As a supplement, we primed subjects with a movie summary before hand (see [Story_Line.pptx](Story_Line.pptx)). 


### Presentation scripts

All presentation scripts used [PsychoPy](https://www.psychopy.org/). This is not included in the `conda` environment, so you will have to download it yourself:

```bash
$ conda activate budapest
$ pip install psychopy
```

*IMPORTANT:* if you are running this code on linux, you might run into issues. try running with an additional line of code, see here:

```bash
$ conda activate budapest
$ pip install https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04/wxPython-4.2.1-cp310-cp310-linux_x86_64.whl
$ pip install psychopy
```

Running a demo/test version outside of the scanner also requires the following package:

```bash
pip install psychopy-mri-emulator
```

All presentation scripts assume that the stimuli are placed in a subdirectory named `stim`.

During the anatomical scan, subjects were shown the last five minutes of the part they saw outside the scanner. This was done so that subjects could select an appropriate volume. The presentation script used for this run is [`scripts/presentation/soundcheck.py`](scripts/presentation/soundcheck.py). The subject can decrease/increase the volume using the buttons `1` and `2` respectively. Once the script has run, it saves the volume level in a json file called `subjectvolume.json`. This is an example of such file

```json
{
 "sid000020": 1.0,
 "sid000021": 0.5,
 "sid000009": 0.75,
}
```

The presentation script used for the functional imaging runs is [`scripts/presentation/show_movie.py`](scripts/presentation/show_movie.py). Some (limited) config values can be defined in the config json file [`scripts/presentation/config.json`](scripts/presentation/config.json). Once the presentation script is loaded, it shows a dialog box to select the subject id and the run number. The volume is automatically selected by loading the volume information stored in `subjectvolume.json`. Log files are stored in a subdirectory named `res`. It's possible to stop the experiment at any point using `CTRL + q`. In that case, the logs are flushed, saved, and moved to a file with suffix `__halted.txt`. 

The logs save detailed timing information (perhaps eccessive) about each frame. By default, useful information for extracting event files is logged with a `BIDS` log level. Thus, one can easily generate a detailed events file by grepping `BIDS`. For example

```bash
$ grep BIDS sub-test_task-movie_run-1_20200916T114100.txt | awk '{for (i=3; i<NF; i++) printf $i"\t";print $NF}' | head -20
onset	duration	frameidx	videotime	lasttrigger
10.008	{duration:.3f}	1	0.000	9.000
10.009	{duration:.3f}	2	0.000	10.008
10.011	{duration:.3f}	3	0.000	10.008
10.013	{duration:.3f}	4	0.000	10.008
10.015	{duration:.3f}	5	0.000	10.008
10.019	{duration:.3f}	6	0.000	10.008
10.021	{duration:.3f}	7	0.000	10.008
10.032	{duration:.3f}	8	0.000	10.008
10.045	{duration:.3f}	9	0.000	10.008
10.059	{duration:.3f}	10	0.033	10.008
10.072	{duration:.3f}	11	0.033	10.008
10.085	{duration:.3f}	12	0.033	10.008
10.099	{duration:.3f}	13	0.067	10.008
10.112	{duration:.3f}	14	0.067	10.008
10.125	{duration:.3f}	15	0.100	10.008
10.139	{duration:.3f}	16	0.100	10.008
10.152	{duration:.3f}	17	0.100	10.008
10.165	{duration:.3f}	18	0.133	10.008
10.179	{duration:.3f}	19	0.133	10.008
```

The available columns are `onset` (frame onset); `duration` (containing a python format string so that duration information can be added with a trivial parser); `frameidx` (index of the frame shown); `videotime` (time of the video); `lasttrigger` (time of the last received trigger).

We provide a simplified events file with the published BIDS dataset. These events file were generated in the notebook  [`notebooks/2020-06-08_make-event-files.ipynb`](notebooks/2020-06-08_make-event-files.ipynb).


## Acknowledgements

Thanks to the original authors, specifically Jiahui Guo !!
