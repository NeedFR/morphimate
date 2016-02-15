# Morphimate
Morphing library and viewer

# Installation

`python setup.py install`

# Usage

The following is an example of creating a morph between two face images.

This will morph between the following two faces:

### Face 1

![Face 1 Image](https://github.com/dramast/morphimate/raw/master/src/morphimate/resources/example/face1.png "Face 1")

### Face 2

![Face 2 Image](https://github.com/dramast/morphimate/raw/master/src/morphimate/resources/example/face2.png "Face 2")

And will product the following output:

### Morphed Output

![Ouput Face](https://github.com/dramast/morphimate/raw/master/src/morphimate/resources/example/morphed.jpg "Output")


```
import csv
import pkg_resources
import numpy as np
from scipy.misc import imread, imsave

from morphimate import Morpher

resource_dir = pkg_resources.resource_filename('morphimate', 'resources')

source = (imread(resource_dir + '/example/face1.png'),
    np.asarray([row for row in csv.reader(open(resource_dir + '/example/points1.csv', 'r'), delimiter=',')]).astype('int')
)

target = (imread(resource_dir + '/example/face2.png'),
    np.asarray([row for row in csv.reader(open(resource_dir + '/example/points2.csv', 'r'), delimiter=',')]).astype('int')
)

midway = Morpher(source, target, 300, 300).morph(0.5, 0.5)

imsave('morphed.jpg', midway)
```



The `MorphimateWidget` class provides a Qt Widget for creating morph animations (See examples below).

# Examples

Two example programs are provided:
- `src/scripts/morhimate_example_1.py`
- `src/scripts/morhimate_example_2.py`

The first example just shows how to create an animation window showing a morph between random colourful images.
This looks (subjectively) pretty but isn't really that useful.

The second example shows an animation window that displays morphing between various paintings of faces.



