<?php
  $filename = $_FILES['file']['name'];

  $meta = $_POST;
  echo $filename . ', size: ' . $_FILES['file']['size'];
  $destination = $meta['targetPath'] . $filename;
  $tempFolder = escapeshellarg($meta['tempFolder']);
  $username = escapeshellarg($meta['username']);
  $experiment = escapeshellarg($meta['experiment']);
  $type = escapeshellarg($meta['type']);
  $species = escapeshellarg($meta['species']);

  move_uploaded_file( $_FILES['file']['tmp_name'] , $destination );

  exec('python parse_vcf.py ' . $destination . ' '. $tempFolder . ' ' .  $username . ' ' . $experiment . ' ' . $species, $out);
?>

