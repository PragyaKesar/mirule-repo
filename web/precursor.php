<?php
require __DIR__ . '/inc/layout.php';
require __DIR__ . '/inc/run.php';
require __DIR__ . '/inc/results.php';
require __DIR__ . '/inc/examples.php';
page_header('Precursor prediction', 'Analysis');
?>
<h2>Prediction of precursor miRNA</h2>
<p>This analysis classifies an input hairpin as a real plant pre-miRNA or a pseudo hairpin.
Enter one sequence of 40 to 600 nt. A FASTA header line is accepted and ignored.</p>
<?php
sequence_form('precursor.php', EXAMPLE_PRECURSOR);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    [$seq, $error] = read_sequence();
    $r = $error ? ['ok' => false, 'error' => $error] : run_mirule(['precursor', $seq]);
    if (!$r['ok']) {
        error_box($r['error']);
    } else {
        echo '<section class="results"><h3>Result summary</h3>';
        echo precursor_table($r);
        echo '<h4>Sequence and RNAfold structure</h4>' . aligned_block($r['sequence'], $r['structure']);
        echo '<h4>Secondary structure</h4><div class="svg">' . $r['svg'] . '</div></section>';
    }
}
page_footer();
