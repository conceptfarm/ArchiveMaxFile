import os
import sys
import platform
import configparser
import traceback

from pathlib import PurePath, Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from MaxZipFile import MaxFileZip
from DarkPalette import QtDarkPalette


palette = QtDarkPalette()
maxFileIconB = b',/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAYABgDASIAAhEBAxEB/8QAGAABAQEBAQAAAAAAAAAAAAAAAAYHBAX/xAAmEAACAQQBAwQDAQAAAAAAAAABAgMABAURIQYSQRMiMWEUUVKB/8QAFwEAAwEAAAAAAAAAAAAAAAAAAgQFA//EAB4RAAICAgIDAAAAAAAAAAAAAAECACEDETGxBCKB/9oADAMBAAIRAxEAPwDaprkW1pNOUdxEjOUQbZtDegPJqEx/WnUvqR317jFhxkkwiCtGVK7P7PO/vWqvZkltoJJpYn7I1LHQ2dAbrKupsjZ3txLkLXKXE1wJQq2M6HUY+GKnegCPNOYgCbEg+dkZE2raI+d9TcMddLcW8Uyb7ZFDD/aVwYSdZcZZyJH6SvCjBP5BUcUpci5TRvUbnpsoZSD8GoXL9JYu2ykVxb4SS6Rve6rKQoOxx2+eN8fFKUSkgzLMiutiVWLubm5Lrd2X4wRU0DyC2vcB9A8b80pShPMNOLn/2Q=='
arrowIconB = b',iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA3ppVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ4IDc5LjE2NDAzNiwgMjAxOS8wOC8xMy0wMTowNjo1NyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo5NUE5NkEyOEYzREFFMTExQTdBQUE1REU2RUIxOEI4OSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpGQTBFNTZDMUYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpGQTBFNTZDMEYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0YTMzYzI1Yi1kMzU0LWFjNDQtOGI1NS05MTViODNmZTAyMDMiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo1ZTBhNjdmYy1lNGJhLWU5NGEtYTEyZS00YWUyODUwNzk1MWQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz5BHBEvAAABIElEQVR42mL8//8/AzUAEwOVAH0NYmRkZAZiURBNtkEgzUz69mbssy4UA7kSuAwjzmt/geiffjL7jAt5uAxjQbJZGkgJ4zLrz+Nvfxhk9JPYp11g+JllMAmo/gUwxv/C9YOiH+x8HaDzOw5sw2bI/98M/3+c/PgTbLM0Pwszw8V5P3MNJgG5cMPgLmL4x8Dw/dCbn/iCC+KyN38ZpPWT2SZcYPhVYNADFHqNahDYsD9EBdmfxy/+MDMy/YMZjmoQKIH//cVIlElvrs/9u9hjKpD1FiWMCAa2tDk3Q8jyDRBDbsxlWOo1FTl8UFwEFHwKpJ5iTUc8HGb/QN5+c3Muw3JfDEOITkf/od7BZQiK1wilbqi332IzhGiDhmYxAhBgAKv1fkydSL9WAAAAAElFTkSuQmCC'
trashIconB = b',iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA3ppVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ4IDc5LjE2NDAzNiwgMjAxOS8wOC8xMy0wMTowNjo1NyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo5NUE5NkEyOEYzREFFMTExQTdBQUE1REU2RUIxOEI4OSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpGQTBCMjI3OEYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpGQTBCMjI3N0YzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0YTMzYzI1Yi1kMzU0LWFjNDQtOGI1NS05MTViODNmZTAyMDMiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo1ZTBhNjdmYy1lNGJhLWU5NGEtYTEyZS00YWUyODUwNzk1MWQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz5CNJ6PAAAAuElEQVR42mL8//8/AzUAC4zByMiILicNxMJY9LwF4qcgBrIjWPBYIgxUeABdEGihA8wgFHGYqUAFuFxACLwFmvGUBc0FB0k1BegAe5ALaeKip6S6CuQakCFYA/v9+/c/yIl+JnSBv3//MoKwkJCQOyE21nSEZBBJbNob9OfPH0ZS2LR30b9//0hi44w1kCIQBqaPQ4TYuPIaPMffuHFjD6F0o6Gh4QJL1dgMwld8YM0aGC6iFAAEGACMCr1EvYhDbgAAAABJRU5ErkJggg=='
trashBIconB = b',iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA3ppVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ4IDc5LjE2NDAzNiwgMjAxOS8wOC8xMy0wMTowNjo1NyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo5NUE5NkEyOEYzREFFMTExQTdBQUE1REU2RUIxOEI4OSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpGQTBCMjI3Q0YzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpGQTBCMjI3QkYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0YTMzYzI1Yi1kMzU0LWFjNDQtOGI1NS05MTViODNmZTAyMDMiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo1ZTBhNjdmYy1lNGJhLWU5NGEtYTEyZS00YWUyODUwNzk1MWQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4SC9lwAAAAu0lEQVR42mL4//8/AzYMBHpA+h06hopjqGeEamJgZGSUBlLCDKSDt0AznrIgCQgDBQ6QagrQAQ5A6inVXMQE44E4IEFyDAExWNAkQN47SIK37EHewmYQw/v373+Q4T0GJnSBv3//MoKwkJCQOyE2sj4WLAaRxKa9Qf/+/WMkhY3ToD9//pDExuciktiD1yCMdARM2YxQfJgQGyWVwzItcsa9cePGHkIpWUNDwwU5r6EYRGIpADcEBAACDAC4Sf/fgI6DSAAAAABJRU5ErkJggg=='
folderIconB = b',iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA3ppVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ4IDc5LjE2NDAzNiwgMjAxOS8wOC8xMy0wMTowNjo1NyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo5NUE5NkEyOEYzREFFMTExQTdBQUE1REU2RUIxOEI4OSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpGQTEyMDA2NUYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpGQTEyMDA2NEYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0YTMzYzI1Yi1kMzU0LWFjNDQtOGI1NS05MTViODNmZTAyMDMiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo1ZTBhNjdmYy1lNGJhLWU5NGEtYTEyZS00YWUyODUwNzk1MWQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7WN5sDAAAAVUlEQVR42mL8//8/AzUAEwOVwOAziAWZc/z48f/i4uIoCl6+fMlgaWnJSMggRmoFNoqL7t27R7Sp6C4lO4zQg2AYR/8gNwgUpaREP00S5DAObIAAAwA9CRzYZT5PIgAAAABJRU5ErkJggg=='
crossIconB = b',iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA3ppVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ4IDc5LjE2NDAzNiwgMjAxOS8wOC8xMy0wMTowNjo1NyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo5NUE5NkEyOEYzREFFMTExQTdBQUE1REU2RUIxOEI4OSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpGQTBFNTZCREYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpGQTBFNTZCQ0YzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0YTMzYzI1Yi1kMzU0LWFjNDQtOGI1NS05MTViODNmZTAyMDMiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo1ZTBhNjdmYy1lNGJhLWU5NGEtYTEyZS00YWUyODUwNzk1MWQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz5FrHaNAAACTUlEQVR42mL8//8/AzUAE7oAIyMjHxArgmhS5JjQFErOV4jwf6vfPE2bU0IdyBdAkhMAiQHlpoLUgNSimATyGtR7IENi/+rWPv2vnP7ig37zPqBGU6A4yDCQIaZAsf3/lTNeANU8AakF6YHpZwQTQKfOlw/zj+NR6fz36RHjX4b/DOwsnEwfeWWuWt+aXg6y5ahaZhf/5ydaP/98/8fCwMjAyCf3b9GXOxWJD1dtBJrxCWaQ4luNwqncX18ZggyBAS6wYdJXQT7j//xU6xvQEJgcyLBP3KLnRG9MyAaa8QDuIm02QfWdIs4tfEyseshe5wUaBqI/IxkCAh/+/brk+WZfzdVf72/CXQQPTFYB1a2imIahA5AhvmBDPtwG6v8A1o+cjmCGbRJ1asVl2Md/vy/5v9lXjWwIxKvogJmNQYCZjen3v39YXSPEzM7IwMSGO0GCXcMhpnpUKbGbm4lF7y/DPwZsmIuJWR+opgukFiWdwQObXVT9qFJCD8vXZ1pv//z4hy+MhFk4mP5wS121vreg9OrP1zdRo1+zaDrL1xfG6IZ8AoYJIzDd8jKx6mMaJnFG+HpfFtCM+zCvvV356tiSl3++ffsHTEcwDIqdiLeHqsLfHqr++O/XRWQ5kNqVr44uAemFhxHIaVlvT+xd/+1R9R+Gfz9ghkS9PVx14/fH2yAc+fZwNUgMJAdSs+7bo6qstyf3gfSi5DVYfuvgN4o5Lu61WYOVH5zPkOQEQGIguXZ+o2jkfAbPa+hFBSiWgfgd3DZi5KhVsAEEGADYR21ldAGYcwAAAABJRU5ErkJggg=='
tickIconB = b',iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA3ppVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ4IDc5LjE2NDAzNiwgMjAxOS8wOC8xMy0wMTowNjo1NyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo5NUE5NkEyOEYzREFFMTExQTdBQUE1REU2RUIxOEI4OSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpGQTBFNTZCOUYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpGQTBFNTZCOEYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0YTMzYzI1Yi1kMzU0LWFjNDQtOGI1NS05MTViODNmZTAyMDMiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo1ZTBhNjdmYy1lNGJhLWU5NGEtYTEyZS00YWUyODUwNzk1MWQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7r+VMlAAAB/0lEQVR42mL8//8/AzUAEwOVAMkGMTIygjAXRQYBDeBk4OY2YJ0xwx/IlkaRBIURMRgIOBhYWfU5Hj9ezPbv3yv2nTvzgGJScHksGhixiLGDDXnwYB7zhz+vGC7ffc76798Ltm3bcoBy/CA1TGhOF2UUFTUA0UhibEBKhOPmzezfAlI+fx/c/cvw9w/D7yt3//83NnYAygmghBFQgxhLXZ0FyOnAMHAB8iWAmBUoJcpx+3bVbz6pgL+3b/9l+P2HAYxfvTr928i4HSj/Fh5GIFOZKyu92H7+vM144eZLtj9/HrNMmRIGFJdmu359IvOrL68Zjl94Ace7Dm1lkJU3AcrzwbwPDg+gzcpsHz7M+X3ridb/Xz//M7CwMLCZaP9kePr0wD92Ie8/d279gfv/y+dLDDlp1Qx3bt0C6v0I9xHUIAHG8GjT/ynpfQwsrGJgGaBhzBJSzH+fPPoLN+TrlysMRbmVDLdugAz5gBy+LFDvfQAadhHILGVITO0BGibK8PcXw9+HDxCGfPt2naGhqgabIXCDoIa9Ahp2DuiSMoao2F6gYUJwVd+/32JorK5kOH/2BjZDsCZIIBBniE30Zdi8+zbD9v2vGNZtO85gbmUDFBfCm2BxpGJxxsRUP4bVm3Yy2NjbEjIEHms48hU/kBIGpRPk2MGZDwddeQQQYADaYF4FCdDyhAAAAABJRU5ErkJggg=='
diskIconB = b',iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA3ppVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ4IDc5LjE2NDAzNiwgMjAxOS8wOC8xMy0wMTowNjo1NyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo5NUE5NkEyOEYzREFFMTExQTdBQUE1REU2RUIxOEI4OSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpGQTEyMDA2MUYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpGQTEyMDA2MEYzMEMxMUVBODVDQkZEMzM1MERDRjUzNiIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0YTMzYzI1Yi1kMzU0LWFjNDQtOGI1NS05MTViODNmZTAyMDMiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo1ZTBhNjdmYy1lNGJhLWU5NGEtYTEyZS00YWUyODUwNzk1MWQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4zKQsUAAABcUlEQVR42mL8//8/AzUAC4hgZGSUBlLCJOh7C8QvgY74g2IQyBDO//8PEGvK/+vXF/zQ0uoFOgBuGMwghu/X7v+Aq9RW8oCzr97bgS7O8u//Ho5r1xiQDWOCK/r7jxGOQbb+/38JmzgI/Lly9+8fFc1YoGHFQK44iosY/v3FHhZ6Ku5oYSMMUvvn2q0/DBqasUD+AiB+ijDoL6pBQCfrYTFYGFntn6vXMQIbxSBgwB/EF9jfT1/5gTX6oQbBw+D7iYs/CUQcI26D/v2D0LduzGLITV/H8OXzP6xG8PAyMUyeGcSgppGGy0UQuiATbAg7Du/9ZGS0Z6gs3sCwahMug/5AnPvxI8glb8EacKXqF8+F4eoxDYL4hFFKiuX/s2fCQBcdwuEiO0YlJbb/f//hDyOgIX+gLrLD5aL/9+4Jw8MUw6D//zDTC3YgjEU9iovAfgZ66TAxGffnjgMoSYQRVB6RUYygevX//6eM1CrYAAIMACmFt5+RSYJwAAAAAElFTkSuQmCC'


#################
## WORKER CLASS
#################

class WorkerSignals(QObject):
	started = pyqtSignal()
	finished = pyqtSignal()
	error = pyqtSignal()
	result = pyqtSignal(object)
	progressTuple = pyqtSignal(tuple)
	progressInt = pyqtSignal(int)
	progressFloat = pyqtSignal(float)
	progressNone = pyqtSignal()

class Worker(QRunnable):
	def __init__(self, fn, progressType=None, *args, **kwargs):
		super().__init__()

		# Store constructor arguments (re-used for processing)
		self.setAutoDelete(True)
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()

		# Add the callback to our kwargs
		self.kwargs['progress_callback'] = None
		if progressType == 'tuple':
			self.kwargs['progress_callback'] = self.signals.progressTuple
		elif progressType == 'int':
			self.kwargs['progress_callback'] = self.signals.progressInt
		elif progressType == 'float':
			self.kwargs['progress_callback'] = self.signals.progressFloat
		elif progressType == None:
			self.kwargs['progress_callback'] = self.signals.progressNone
		
	
	@pyqtSlot()
	def run(self):
		'''
		Initialise the runner function with passed args, kwargs.
		'''
		
		# Retrieve args/kwargs here; and fire processing using them
		try:
			self.signals.started.emit()
			result = self.fn(*self.args, **self.kwargs)
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			#self.signals.error.emit((exctype, value, traceback.format_exc()))
			self.signals.error.emit()
		else:
			self.signals.result.emit(result)  # Return the result of the processing
		finally:
			self.signals.finished.emit()  # Done


#####################
## DELEGATES
#####################

class ProgressDelegate(QStyledItemDelegate):
	def paint(self, painter, option, index):
		progress = index.data(Qt.UserRole+1000)
		opt = QStyleOptionProgressBar()
		opt.rect = option.rect
		opt.minimum = 0
		opt.maximum = 100

		opt.progress = progress
		opt.text = "{}%".format(progress)
		opt.textAlignment = Qt.AlignCenter
		opt.textVisible = True
		QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)


class IconDelegate(QStyledItemDelegate):
	def __init__(self, Parent=None):
		super().__init__()
		
		self.emptyIcon = QIcon(QApplication.style().standardIcon(QStyle.SP_CustomBase))
		self.goodIcon = QIcon(QApplication.style().standardIcon(QStyle.SP_DialogApplyButton))
		self.errorIcon = QIcon(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical))
		self.processingIcon = QIcon(QApplication.style().standardIcon(QStyle.SP_ArrowRight))

		self._iconDict = {'empty':self.emptyIcon,'good':self.goodIcon,'error':self.errorIcon,'proc':self.processingIcon}
	

	def paint(self, painter, option, index):
		d = index.data(Qt.UserRole+1001)
		icon = self._iconDict[d]
		option.rect = option.rect.adjusted(5,5,-5,-5)
		#option.rect.setSize(QSize(15,15))
		icon.paint(painter, option.rect, Qt.AlignCenter)


#####################
## MAIN WINDOW CLASS
#####################

class MainWindow(QMainWindow):
	
	def __init__(self, droppedFiles, zipFileDir):
		super().__init__()
		self.left = 150
		self.top = 150
		self.width = 800
		self.height = 480
		self.droppedFiles = droppedFiles
		self.zipFileDir = zipFileDir
		self.threadpool = QThreadPool().globalInstance()
		self.threadpoolQLength = 0
		self.threadpool.setMaxThreadCount(1)

		self.okIcon = QIcon(self.style().standardIcon(QStyle.SP_CustomBase))
		self.okPix = QPixmap(self.okIcon.pixmap(QSize(13, 13)))
		self.goodIcon = QIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
		self.goodPix = QPixmap(self.goodIcon.pixmap(QSize(13, 13)))
		self.badIcon = QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical))
		self.badPix = QPixmap(self.badIcon.pixmap(QSize(13, 13)))
		self.processingIcon = QIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
		self.processingPix = QPixmap(self.processingIcon.pixmap(QSize(13, 13)))
		self.removeIcon = QIcon(self.style().standardIcon(QStyle.SP_DockWidgetCloseButton))
		self.removePix = QPixmap(self.removeIcon.pixmap(QSize(19, 19)))
		self.folderIcon = QIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
		self.folderPix = QPixmap(self.folderIcon.pixmap(QSize(19, 19)))
		self.maxFilePix = QPixmap()
		self.maxFilePix.loadFromData(QByteArray.fromBase64(maxFileIconB))
		
		self.setupUi(self)

	def setupUi(self, MainWindow):
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setWindowTitle('Max File Archiver')
		self.centralwidget = QWidget(MainWindow)
		self.centralwidget.setObjectName('centralwidget')
		
		self.verticalLayout = QVBoxLayout(self.centralwidget)
		self.verticalLayout.setObjectName('verticalLayout')
		
		self.scriptFiles_gl = QGridLayout()
		self.scriptFiles_gl.setContentsMargins(-1, -1, -1, 8)
		self.scriptFiles_gl.setSpacing(6)
		self.scriptFiles_gl.setObjectName('scriptFiles_gl')

		self.w = QTableWidget(0,4)
		self.w.setObjectName('table')
		self.w.setSelectionMode(QAbstractItemView.NoSelection)
		self.w.setState(QAbstractItemView.NoState)
		self.w.setShowGrid(False)

		self.progDelegate = ProgressDelegate(self.w)
		self.iconDelegate = IconDelegate(self.w)
		self.w.setItemDelegateForColumn(2, self.progDelegate)
		self.w.setItemDelegateForColumn(0, self.iconDelegate)
		self.w.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
		self.w.horizontalHeader().hide()
		self.w.verticalHeader().hide()
		self.w.setColumnWidth(0,10)
		self.w.setColumnWidth(2,250)
		
		self.model = QStandardItemModel(0, 3)
		self.addFilesToView(self.droppedFiles, self.w)
		
		self.scriptFiles_gl.addWidget(self.w, 0, 0, 1, 1)	
		
		#ADD MORE AREA
		self.gridLayoutAddMore = QGridLayout()
		self.gridLayoutAddMore.setContentsMargins(0, 0, 0, 0)
		
		self.dragAndDropLabel_1 = QLabel("Drag and Drop 3ds Max Files here", self)
		self.dragAndDropLabel_1.setMinimumSize(QSize(120, 60))
		self.dragAndDropLabel_1.setAlignment(Qt.AlignCenter)
		
		self.dragAndDropLabel_2 = QLabel("", self)
		self.dragAndDropLabel_2.setFixedSize(QSize(32, 60))
		self.dragAndDropLabel_2.setAlignment(Qt.AlignCenter)
		self.dragAndDropLabel_2.setPixmap(self.maxFilePix)
		
		sI = QSpacerItem(40, 40,QSizePolicy.Expanding, QSizePolicy.Minimum)
		sI2 = QSpacerItem(40, 40,QSizePolicy.Expanding, QSizePolicy.Minimum)
		
		self.gridLayoutAddMore.addItem(sI, 1, 0, 1, 1)
		self.gridLayoutAddMore.addWidget(self.dragAndDropLabel_2, 1, 1, 1, 1)
		self.gridLayoutAddMore.addWidget(self.dragAndDropLabel_1, 1, 2, 1, 1)
		self.gridLayoutAddMore.addItem(sI2, 1, 3, 1, 1)

		#OUTPUT DIR AREA
		self.processDir_gl = QGridLayout()
		self.processDir_gl.setContentsMargins(0, 8, 0, 8)
		self.processDir_gl.setSpacing(6)
		self.processDir_gl.setObjectName('processDir_gl')
		self.processDir_gl.setColumnMinimumWidth(3, 140)

		self.singleZipFile_chb = QCheckBox('Archive to Single File', self.centralwidget)
		self.singleZipFile_chb.setCheckState(False)
		#self.singleZipFile_chb.setMinimumSize(QSize(180, 22))

		self.maxFilesDir_txt = QLineEdit(self.zipFileDir, self.centralwidget)
		sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.maxFilesDir_txt.sizePolicy().hasHeightForWidth())
		self.maxFilesDir_txt.setSizePolicy(sizePolicy)
		self.maxFilesDir_txt.setMinimumSize(QSize(0, 22))
		self.maxFilesDir_txt.setObjectName('maxFilesDir_txt')
		
		self.maxFilesDir_lbl = QLabel(self.centralwidget)
		self.maxFilesDir_lbl.setText('Save Archive Zip Files To:')
		self.maxFilesDir_lbl.setMinimumSize(QSize(130, 22))
		self.maxFilesDir_lbl.setObjectName('maxFilesDir_lbl')
		
		self.maxFilesDir_btn = QPushButton(self.centralwidget)
		self.maxFilesDir_btn.setText('...')
		self.maxFilesDir_btn.setMinimumSize(QSize(40, 22))
		self.maxFilesDir_btn.setMaximumSize(QSize(40, 16777215))
		self.maxFilesDir_btn.setObjectName('maxFilesDir_btn')

		
		self.processDir_gl.addWidget(self.maxFilesDir_lbl, 0, 0, 1, 1)
		self.processDir_gl.addWidget(self.maxFilesDir_txt, 0, 1, 1, 1)
		self.processDir_gl.addWidget(self.maxFilesDir_btn, 0, 2, 1, 1)
		self.processDir_gl.addWidget(self.singleZipFile_chb, 0, 3, 1, 1, Qt.AlignRight)
		self.processDir_gl.setColumnStretch(1, 1)

		#PROCESS BUTTON AREA
		self.process_gl = QGridLayout()
		self.process_gl.setContentsMargins(-1, -1, -1, 8)
		self.process_gl.setSpacing(6)
		
		self.process_btn = QPushButton(self.centralwidget)
		self.process_btn.setText('Archive')
		self.process_btn.setMinimumSize(QSize(80, 40))
		self.process_btn.setMaximumSize(QSize(16777215, 40))
		self.process_btn.setLayoutDirection(Qt.LeftToRight)
		self.process_btn.setObjectName('process_btn')
		
		if Path(self.zipFileDir).is_dir() == False:
			self.process_btn.setEnabled(False)

		self.process_gl.addWidget(self.process_btn, 1, 1, 1, 1)
		self.process_gl.setColumnStretch(1, 1)
			
		self.verticalLayout.addLayout(self.gridLayoutAddMore)
		self.verticalLayout.addLayout(self.scriptFiles_gl)
		self.verticalLayout.addLayout(self.processDir_gl)
		self.verticalLayout.addLayout(self.process_gl)

		MainWindow.setCentralWidget(self.centralwidget)
		QMetaObject.connectSlotsByName(self)
		
		# Enable dragging and dropping onto the GUI
		self.setAcceptDrops(True)
		self.show()	
	


	######################
	## FUNCTIONS        ##
	######################

	def addFilesToView(self, files, view):
		existingRows = view.rowCount()
		for r, (file) in enumerate(files):
			newRow = r + existingRows
			it_id = QTableWidgetItem()
			it_id.setData(Qt.UserRole+1001, 'empty')
			it_file = QTableWidgetItem(file)
			it_progress = QTableWidgetItem()
			it_progress.setData(Qt.UserRole+1000, 0)
			it_button = QTableWidgetItem()
			
			view.insertRow(view.rowCount())
			
			for c, item in enumerate((it_id, it_file, it_progress, it_button)):
				view.setItem(newRow, c, item)
				if c!=3: item.setFlags(Qt.NoItemFlags)
				newButton = QPushButton('Remove', self.w)
				newButton.clicked.connect(self.tableButtonClick)
				view.setCellWidget(newRow,3,newButton)
		
	def writeToConfig(self, setting, key, value):
		#config = configparser.ConfigParser()
		config.read(configFileName)
		config.set(setting, key, value)
		
		with open(configFileName, 'w') as configfile:
			config.write(configfile)

	def setPBData(self,row,data):
		self.w.item(row,2).setData(Qt.UserRole+1000,data)

	def setIconData(self, row, data):
		self.w.item(row,0).setData(Qt.UserRole+1001,data)

	def setFinishedData(self, row, data):
		existingData = self.w.item(row,0).data(Qt.UserRole+1001)
		
		if(existingData != 'error'):
			self.w.item(row,0).setData(Qt.UserRole+1001,data)
		
		if (self.threadpool.activeThreadCount()) == 0:
			self.setEnabledControlls(True)

	def maxZipFiles(self, file):
		maxZip = MaxFileZip(file, (file+'.zip'), True)

	def setEnabledControlls(self, state):
		self.w.setEnabled(state)
		self.maxFilesDir_btn.setEnabled(state)
		self.maxFilesDir_txt.setEnabled(state)
		self.process_btn.setEnabled(state)
		self.setAcceptDrops(state)
	
	def resetProgressBars(self):
		for row in range(self.w.rowCount()):
			self.setPBData(row, 0)

	######################
	## BUTTON FUNCTIONS ##
	######################
	
	def tableButtonClick(self):
		r = (self.sender().parent().parent().currentRow())
		self.sender().parent().parent().removeRow(r)
	
	@pyqtSlot()
	def on_maxFilesDir_btn_clicked(self):
		defaultDir = self.maxFilesDir_txt.text() if self.maxFilesDir_txt.text() != '' else QDir.home().dirName()
		dirPath = QFileDialog.getExistingDirectory(self, 'Select a directory',defaultDir, QFileDialog.ShowDirsOnly)
		
		if dirPath:
			self.maxFilesDir_txt.setText(dirPath)
			self.writeToConfig('ArchiveMaxSettings', 'zipFileDir', dirPath)

	@pyqtSlot(str)
	def on_maxFilesDir_txt_textEdited(self, text):
		if Path(text).is_dir() == False:
			self.process_btn.setEnabled(False)
		else:
			self.process_btn.setEnabled(True)

	@pyqtSlot()
	def on_process_btn_clicked(self):
		self.resetProgressBars()
		self.setEnabledControlls(False)
		
		for row in range(self.w.rowCount()):
			#print(self.w.item(row,1).data(0))
			fileToZip = self.w.item(row,1).data(0)
			thisProgBar = self.w.item(row,2)
			

			maxZip = MaxFileZip(fileToZip, (fileToZip+'.zip'), True)
			
			
			worker = Worker(maxZip.main,'float')
			#worker.signals.progressFloat.connect(lambda i,r=row: self.w.item(r,2).setData(Qt.UserRole+1000,i))
			worker.signals.started.connect(lambda r=row: self.setIconData(r,'proc')) #self.w.item(r,0).setData(Qt.UserRole+1001,'proc'))
			worker.signals.progressFloat.connect(lambda i,r=row: self.setPBData(r,i))
			worker.signals.error.connect(lambda r=row: self.setIconData(r,'error'))
			worker.signals.finished.connect(lambda r=row: self.setFinishedData(r,'good'))
			'''
			worker.signals.result.connect(self.logText.appendPlainText)
			worker.signals.error.connect(self.errorPB)
			worker.signals.finished.connect(self.threadComplete)
			'''


			self.threadpool.start(worker)


	###########################
	## DRAG + DROP FUNCTIONS ##
	###########################
	# The following three methods set up dragging and dropping for the app
	def dragEnterEvent(self, e):
		if e.mimeData().hasUrls:
			e.accept()
		else:
			e.ignore()

	def dragMoveEvent(self, e):
		if e.mimeData().hasUrls:
			e.accept()
		else:
			e.ignore()

	def dropEvent(self, e):
		'''
		Drop files directly onto the widget
		File locations are stored in fname
		:param e:
		:return:
		'''
		newFiles = []
		if e.mimeData().hasUrls:
			e.setDropAction(Qt.CopyAction)
			e.accept()
			for url in e.mimeData().urls():
				fname = str(url.toLocalFile())
				if PurePath(fname).suffix == '.max':
					newFiles.append(fname)

			self.addFilesToView(newFiles,self.w)
			self.droppedFiles = self.droppedFiles + newFiles
		else:
			e.ignore()


if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
	app.setPalette(palette)

	#dirList = []
	dirList = ['C:\\Python37\\15-01-21_CIYE_Set.max','C:\\Python37\\assetTest.max','C:\\Python37\\field_skin.max']
	
	for arg in sys.argv:
		if PurePath(arg).suffix == '.max':
			dirList.append(arg)
	
	#sort the list , chech the code below make sure it's right
	dirList = sorted(dirList, key=lambda i: (os.path.basename(i)))
	
	configFileName = 'ArchiveMax.ini'
	config = configparser.ConfigParser()

	zipFileDir = ''
	
	#appIcon = icons.qIconFromBase64(icons.appIconBase64)
	
	try:
		config.read(configFileName)
		zipFileDir = (config['ArchiveMaxSettings']['zipFileDir'])
	except:
		print('Didnt Pass')
		config['ArchiveMaxSettings'] = {'zipFileDir':''}
		with open(configFileName, 'w') as configfile:
			config.write(configfile)



	ex = MainWindow(dirList, zipFileDir)
	sys.exit(app.exec_())