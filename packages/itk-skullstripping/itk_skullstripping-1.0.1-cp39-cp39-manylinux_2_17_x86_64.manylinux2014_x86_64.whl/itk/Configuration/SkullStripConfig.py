depends = ('ITKPyBase', 'ITKRegistrationCommon', 'ITKLevelSets', 'ITKImageIntensity', 'ITKIOVTK', 'ITKIOTransformMatlab', 'ITKIOTransformInsightLegacy', 'ITKIOTransformHDF5', 'ITKIOTIFF', 'ITKIOStimulate', 'ITKIOPNG', 'ITKIONRRD', 'ITKIONIFTI', 'ITKIOMeta', 'ITKIOMeta', 'ITKIOLSM', 'ITKIOJPEG', 'ITKIOImageBase', 'ITKIOGIPL', 'ITKIOGDCM', 'ITKIOBioRad', 'ITKIOBMP', )
templates = (  ('StripTsImageFilter', 'itk::StripTsImageFilter', 'itkStripTsImageFilterISS3ISS3', True, 'itk::Image< signed short,3 >, itk::Image< signed short,3 >'),
  ('StripTsImageFilter', 'itk::StripTsImageFilter', 'itkStripTsImageFilterIUC3IUC3', True, 'itk::Image< unsigned char,3 >, itk::Image< unsigned char,3 >'),
  ('StripTsImageFilter', 'itk::StripTsImageFilter', 'itkStripTsImageFilterIUS3IUS3', True, 'itk::Image< unsigned short,3 >, itk::Image< unsigned short,3 >'),
  ('StripTsImageFilter', 'itk::StripTsImageFilter', 'itkStripTsImageFilterIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
  ('StripTsImageFilter', 'itk::StripTsImageFilter', 'itkStripTsImageFilterID3ID3', True, 'itk::Image< double,3 >, itk::Image< double,3 >'),
)
factories = ()
