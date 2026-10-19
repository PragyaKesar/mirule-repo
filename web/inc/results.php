<?php
// Rendering helpers for result pages.

function aligned_block($seq, $ss, $mark_from = 0, $mark_to = 0) {
    // Sequence over structure in 60 nt rows; optional 1-based highlight.
    $html = '<div class="aligned">';
    for ($i = 0; $i < strlen($seq); $i += 60) {
        $s = '';
        for ($j = $i; $j < min($i + 60, strlen($seq)); $j++) {
            $c = h($seq[$j]);
            $s .= ($mark_from && $j + 1 >= $mark_from && $j + 1 <= $mark_to) ? "<mark>$c</mark>" : $c;
        }
        $html .= '<span class="pos">' . ($i + 1) . '</span>' . $s . "\n";
        $html .= '<span class="pos"></span>' . h(substr($ss, $i, 60)) . "\n";
    }
    return $html . '</div>';
}

function probability_bar($p) {
    $pct = round($p * 100);
    return '<div class="prob"><div class="prob-fill" style="width:' . $pct . '%"></div></div>'
         . '<span class="prob-label">' . number_format($p, 3) . '</span>';
}

function verdict($r) {
    if ($r['is_precursor']) {
        return '<span class="verdict yes">Predicted real pre-miRNA</span>';
    }
    return '<span class="verdict no">Predicted pseudo hairpin</span>';
}

function precursor_table($r) {
    $rows = [
        'Input length' => $r['length'] . ' nt',
        'Prediction' => verdict($r),
        'Probability of real pre-miRNA' => probability_bar($r['probability']),
        'Minimum free energy (MFE)' => number_format($r['mfe'], 2) . ' kcal/mol',
        'Ensemble free energy' => number_format($r['efe'], 2) . ' kcal/mol',
        'GC content' => number_format($r['gc'], 2) . ' %',
        'MFE index 1 (MFE / GC%)' => number_format($r['mfei1'], 3),
        'Base pairs' => $r['base_pairs'],
        'Hairpin loops' => $r['hairpins'],
    ];
    $html = '<table class="result">';
    foreach ($rows as $k => $v) {
        $html .= '<tr><th>' . h($k) . '</th><td>' . $v . '</td></tr>';
    }
    return $html . '</table>';
}
