<?php
  $filename = $_FILES['file']['name'];

  $meta = $_POST;
  echo $filename . ', size: ' . $_FILES['file']['size'];
  $destination = $meta['targetPath'] . $filename;
  move_uploaded_file( $_FILES['file']['tmp_name'] , $destination );

  // Giusto una prova
  //exec('python prova.py ' . $destination, $out);
?>

