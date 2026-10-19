<?php
require __DIR__ . '/inc/layout.php';
require __DIR__ . '/inc/run.php';
require __DIR__ . '/inc/results.php';
require __DIR__ . '/inc/examples.php';
page_header('Precursor from primary sequence', 'Analysis');

$ranges = [];
for ($lo = 60; $lo < 400; $lo += 20) {
    $ranges[] = [$lo, $lo + 20];
}
$chosen = isset($_POST['range']) ? (string)$_POST['range'] : '100-120';
$select = '<label for="range">Precursor length range (nt):</label> <select id="range" name="range">';
foreach ($ranges as [$a, $b]) {
    $v = "$a-$b";
    $select .= '<option value="' . $v . '"' . ($v === $chosen ? ' selected' : '') . ">$a to $b</option>";
}
$select .= '</select>';
?>
<h2>Prediction of precursor from primary sequence</h2>
<p>This analysis scans a primary transcript of 100 to 1,500 nt. Windows within the chosen
length range are folded and scored by the precursor classifier. Up to five of the best non-overlapping
windows are reported.</p>
<?php
sequence_form('primary.php', EXAMPLE_PRIMARY, $select);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    [$seq, $error] = read_sequence();
    if (!$error && !preg_match('/^(\d{2,3})-(\d{2,3})$/', $chosen, $m)) {
        $error = 'Please choose a length range from the list.';
    }
    $r = $error ? ['ok' => false, 'error' => $error] : run_mirule(['primary', $seq, $m[1], $m[2]]);
    if (!$r['ok']) {
        error_box($r['error']);
    } else {
        $b = $r['top'][0];
        echo '<section class="results"><h3>Result summary</h3><table class="result">';
        echo '<tr><th>Input length</th><td>' . h($r['length']) . ' nt</td></tr>';
        echo '<tr><th>Windows scanned</th><td>' . h($r['windows_scanned']) . ' (lengths ' . h($r['range'][0]) . ' to ' . h($r['range'][1]) . ' nt, step ' . h($r['step']) . ' nt)</td></tr>';
        echo '<tr><th>Best window</th><td>' . h($b['start']) . ' to ' . h($b['end']) . ' (' . h($b['length']) . ' nt)</td></tr>';
        echo '<tr><th>Probability of real pre-miRNA</th><td>' . probability_bar($b['probability']) . '</td></tr></table>';
        echo '<h4>Top non-overlapping windows</h4><table class="result compact"><tr><th>Rank</th><th>Start</th><th>End</th><th>Length</th><th>MFE (kcal/mol)</th><th>Probability</th></tr>';
        foreach ($r['top'] as $i => $t) {
            echo '<tr><td>' . ($i + 1) . '</td><td>' . h($t['start']) . '</td><td>' . h($t['end']) . '</td><td>' . h($t['length']) . '</td><td>' . number_format($t['mfe'], 2) . '</td><td>' . number_format($t['probability'], 3) . '</td></tr>';
        }
        echo '</table><h4>Best window: sequence and structure</h4>' . aligned_block($r['best_sequence'], $r['best_structure']);
        echo '<h4>Best window: secondary structure</h4><div class="svg">' . $r['best_svg'] . '</div></section>';
    }
}
page_footer();
