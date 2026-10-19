<?php
// Shared layout and helpers for the miRULE pages.

function h($text) {
    return htmlspecialchars((string)$text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function page_header($title, $active) {
    $nav = ['index.php' => 'Home', 'precursor.php' => 'Analysis', 'team.php' => 'Team', 'help.php' => 'Help'];
    $tools = [
        'precursor.php' => 'Precursor prediction',
        'mature.php'    => 'Mature miRNA identification',
        'primary.php'   => 'Precursor from primary sequence',
    ];
    $self = basename($_SERVER['SCRIPT_NAME']);
    ?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= h($title) ?> · miRULE</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="page">
  <header class="banner">
    <h1>The miRULE webserver</h1>
    <p>Prediction of plant miRNA precursors and mature miRNAs</p>
  </header>
  <nav class="navbar">
    <?php foreach ($nav as $href => $label): ?>
      <a href="<?= $href ?>" class="<?= $active === $label ? 'active' : '' ?>"><?= $label ?></a>
    <?php endforeach; ?>
  </nav>
  <div class="layout">
    <aside class="sidenav">
      <div class="sidenav-title">Analysis tools</div>
      <?php foreach ($tools as $href => $label): ?>
        <a href="<?= $href ?>" class="<?= $self === $href ? 'current' : '' ?>">&#9706; <?= $label ?></a>
      <?php endforeach; ?>
    </aside>
    <main class="content">
<?php
}

function page_footer() {
    ?>
    </main>
  </div>
  <footer class="footer">Developed at the Agriculture Knowledge Management Unit, ICAR–IARI, New Delhi (2018–2019). Revised 2026.</footer>
</div>
<script>
document.querySelectorAll('[data-example]').forEach(function (btn) {
  btn.addEventListener('click', function () {
    document.getElementById('sequence').value = btn.getAttribute('data-example');
  });
});
</script>
</body>
</html>
<?php
}

function sequence_form($action, $example, $extra = '') {
    $value = isset($_POST['sequence']) ? $_POST['sequence'] : '';
    ?>
<form method="post" action="<?= h($action) ?>" class="query">
  <label for="sequence">Sequence (RNA or DNA, plain or FASTA):</label>
  <textarea id="sequence" name="sequence" maxlength="5000" spellcheck="false" required><?= h($value) ?></textarea>
  <?= $extra ?>
  <div class="buttons">
    <button type="submit">Submit query</button>
    <button type="button" class="secondary" data-example="<?= h($example) ?>">Load example</button>
    <a class="button secondary" href="<?= h($action) ?>">Reset</a>
  </div>
</form>
<?php
}

function error_box($message) {
    echo '<div class="error">' . h($message) . '</div>';
}
