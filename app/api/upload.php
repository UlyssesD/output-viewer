<?php
  $filename = $_FILES['file']['name'];

  $meta = $_POST;
  echo $filename . ', size: ' . $_FILES['file']['size'];
  $destination = $meta['targetPath'] . $filename;
  $username = escapeshellarg($meta['username']);
  $experiment = escapeshellarg($meta['experiment']);
  $type = escapeshellarg($meta['type']);
  $species = escapeshellarg($meta['species']);

  move_uploaded_file( $_FILES['file']['tmp_name'] , $destination );

  exec('python prova.py ' . $destination . ' '.  $username . ' ' . $experiment . ' ' . $species, $out);
?>

