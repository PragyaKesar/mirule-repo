<?php
require __DIR__ . '/inc/layout.php';
require __DIR__ . '/inc/run.php';
require __DIR__ . '/inc/results.php';
require __DIR__ . '/inc/examples.php';
page_header('Mature miRNA identification', 'Analysis');
?>
<h2>Identification of mature miRNA from its precursor</h2>
<p>This analysis first checks that the input is a real pre-miRNA. It then scores every
candidate start position and reports the most probable mature miRNA start sites. Enter one
precursor of 60 to 600 nt.</p>
<p class="note">This module is experimental. On held-out plant precursors, the top ranked start
matches an annotated mature start in 7% of cases, and lies within 2 nt in 16%. Use the top
three candidates as hypotheses for validation.</p>
<?php
sequence_form('mature.php', EXAMPLE_MATURE);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    [$seq, $error] = read_sequence();
    $r = $error ? ['ok' => false, 'error' => $error] : run_mirule(['mature', $seq]);
    if (!$r['ok']) {
        error_box($r['error']);
    } else {
        echo '<section class="results"><h3>Result summary</h3>';
        echo precursor_table($r);
        if (!$r['is_precursor']) {
            echo '<p class="note">The input was not predicted as a real precursor, so no mature miRNA is reported.</p>';
            $best = null;
        } else {
            $best = $r['candidates'][0];
            echo '<h4>Predicted mature miRNA</h4><table class="result">';
            echo '<tr><th>Mature sequence (21 nt)</th><td class="mono">' . h($best['mature']) . '</td></tr>';
            echo '<tr><th>Position</th><td>' . h($best['start']) . ' to ' . h($best['end']) . ' (' . h($best['arm']) . ' arm)</td></tr>';
            echo '<tr><th>Probability of start site</th><td>' . probability_bar($best['probability']) . '</td></tr></table>';
            echo '<h4>Top candidate start sites</h4><table class="result compact"><tr><th>Rank</th><th>Start</th><th>Arm</th><th>Sequence (21 nt)</th><th>Probability</th></tr>';
            foreach ($r['candidates'] as $i => $c) {
                echo '<tr><td>' . ($i + 1) . '</td><td>' . h($c['start']) . '</td><td>' . h($c['arm']) . '</td><td class="mono">' . h($c['mature']) . '</td><td>' . number_format($c['probability'], 3) . '</td></tr>';
            }
            echo '</table>';
        }
        echo '<h4>Sequence and RNAfold structure</h4>';
        echo $best ? aligned_block($r['sequence'], $r['structure'], $best['start'], $best['end'])
                   : aligned_block($r['sequence'], $r['structure']);
        echo '<h4>Secondary structure</h4><div class="svg">' . $r['svg'] . '</div></section>';
    }
}
page_footer();
