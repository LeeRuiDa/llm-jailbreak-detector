$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

function Get-Color([string]$hex) {
    $clean = $hex.TrimStart('#')
    [System.Drawing.Color]::FromArgb(
        255,
        [Convert]::ToInt32($clean.Substring(0, 2), 16),
        [Convert]::ToInt32($clean.Substring(2, 2), 16),
        [Convert]::ToInt32($clean.Substring(4, 2), 16)
    )
}

function New-Canvas([int]$width, [int]$height) {
    $bmp = New-Object System.Drawing.Bitmap $width, $height
    $bmp.SetResolution(300, 300)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear((Get-Color '#FFFFFF'))
    @{ Bitmap = $bmp; Graphics = $g }
}

function New-RoundedRectPath([float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = $r * 2
    $path.AddArc($x, $y, $d, $d, 180, 90)
    $path.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
    $path.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
    $path.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
    $path.CloseFigure()
    $path
}

function New-TextFormat {
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $format.Trimming = [System.Drawing.StringTrimming]::Word
    $format
}

function Draw-FittedText {
    param(
        $Graphics,
        [string]$Text,
        [System.Drawing.RectangleF]$Rect,
        [int]$MaxFontSize = 28,
        [int]$MinFontSize = 14,
        [string]$FontStyle = 'Regular',
        [string]$Color = '#111827'
    )

    $style = [System.Drawing.FontStyle]::$FontStyle
    $format = New-TextFormat
    $brush = New-Object System.Drawing.SolidBrush (Get-Color $Color)

    for ($size = $MaxFontSize; $size -ge $MinFontSize; $size--) {
        $font = New-Object System.Drawing.Font('Segoe UI', $size, $style)
        $measured = $Graphics.MeasureString($Text, $font, [System.Drawing.SizeF]::new($Rect.Width, 10000), $format)
        if ($measured.Width -le ($Rect.Width + 4) -and $measured.Height -le ($Rect.Height + 4)) {
            $Graphics.DrawString($Text, $font, $brush, $Rect, $format)
            $font.Dispose(); $brush.Dispose(); $format.Dispose(); return
        }
        $font.Dispose()
    }

    $font = New-Object System.Drawing.Font('Segoe UI', $MinFontSize, $style)
    $Graphics.DrawString($Text, $font, $brush, $Rect, $format)
    $font.Dispose(); $brush.Dispose(); $format.Dispose()
}

function Draw-Box {
    param(
        $Graphics,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [string]$Text,
        [string]$Fill = '#F8FAFC',
        [string]$Stroke = '#334155',
        [int]$FontSize = 28,
        [int]$MinFontSize = 15,
        [string]$FontStyle = 'Regular',
        [float]$Radius = 22,
        [int]$Padding = 18
    )

    $path = New-RoundedRectPath $X $Y $Width $Height $Radius
    $fillBrush = New-Object System.Drawing.SolidBrush (Get-Color $Fill)
    $pen = New-Object System.Drawing.Pen (Get-Color $Stroke), 4
    $Graphics.FillPath($fillBrush, $path)
    $Graphics.DrawPath($pen, $path)

    $rect = [System.Drawing.RectangleF]::new($X + $Padding, $Y + $Padding, $Width - 2 * $Padding, $Height - 2 * $Padding)
    Draw-FittedText -Graphics $Graphics -Text $Text -Rect $rect -MaxFontSize $FontSize -MinFontSize $MinFontSize -FontStyle $FontStyle

    $pen.Dispose(); $fillBrush.Dispose(); $path.Dispose()
}

function Draw-Arrow {
    param(
        $Graphics,
        [float]$X1,
        [float]$Y1,
        [float]$X2,
        [float]$Y2,
        [string]$Color = '#475569',
        [float]$Width = 5,
        [switch]$Dashed,
        [string]$Label,
        [float]$LabelX,
        [float]$LabelY
    )

    $pen = New-Object System.Drawing.Pen (Get-Color $Color), $Width
    if ($Dashed) { $pen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash }
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap 7, 8, $true
    $pen.CustomEndCap = $cap
    $Graphics.DrawLine($pen, $X1, $Y1, $X2, $Y2)

    if ($Label) {
        $rect = [System.Drawing.RectangleF]::new($LabelX - 110, $LabelY - 24, 220, 48)
        Draw-FittedText -Graphics $Graphics -Text $Label -Rect $rect -MaxFontSize 20 -MinFontSize 14 -Color '#374151'
    }

    $cap.Dispose(); $pen.Dispose()
}

function Draw-Header {
    param($Graphics, [float]$X, [float]$Y, [float]$Width, [float]$Height, [string]$Text, [string]$Fill)
    Draw-Box -Graphics $Graphics -X $X -Y $Y -Width $Width -Height $Height -Text $Text -Fill $Fill -Stroke '#0F172A' -FontSize 26 -MinFontSize 16 -FontStyle Bold -Radius 20 -Padding 12
}

function Save-Diagram {
    param([scriptblock]$Renderer)
    foreach ($outDir in @('docs/figures', 'thesis_final_tex/figures')) {
        & $Renderer $outDir
    }
}

function Render-Ch3Pipeline {
    param([string]$OutDir)
    $canvas = New-Canvas 2600 1000
    $bmp = $canvas.Bitmap
    $g = $canvas.Graphics

    Draw-Header $g 120 60 2360 110 'Detection Pipeline for the Shipped Runtime' '#DCEAF5'

    $w = 320; $h = 270; $y = 350
    $xs = @(80, 470, 860, 1250, 1640, 2030)
    $fills = @('#EEF2FF', '#E0F2FE', '#ECFCCB', '#FEF3C7', '#FCE7F3', '#E2E8F0')
    $texts = @('Input', 'Text', 'Clean', 'Route', 'Score >= tau', 'Result')

    for ($i = 0; $i -lt $xs.Count; $i++) {
        Draw-Box -Graphics $g -X $xs[$i] -Y $y -Width $w -Height $h -Text $texts[$i] -Fill $fills[$i] -FontSize 20 -MinFontSize 16 -FontStyle Bold
    }

    for ($i = 0; $i -lt $xs.Count - 1; $i++) {
        Draw-Arrow -Graphics $g -X1 ($xs[$i] + $w) -Y1 ($y + $h / 2) -X2 $xs[$i + 1] -Y2 ($y + $h / 2)
    }

    Draw-Box -Graphics $g -X 1315 -Y 690 -Width 220 -Height 130 -Text 'Rules' -Fill '#FFF7ED' -Stroke '#9A3412' -FontSize 22 -MinFontSize 14 -Radius 18 -FontStyle Bold
    Draw-Box -Graphics $g -X 1585 -Y 690 -Width 250 -Height 130 -Text 'LoRA' -Fill '#F5F3FF' -Stroke '#6D28D9' -FontSize 22 -MinFontSize 14 -Radius 18 -FontStyle Bold
    Draw-Arrow -Graphics $g -X1 1410 -Y1 620 -X2 1410 -Y2 690 -Color '#9A3412'
    Draw-Arrow -Graphics $g -X1 1710 -Y1 620 -X2 1710 -Y2 690 -Color '#6D28D9'

    $bmp.Save((Join-Path $OutDir 'ch3_pipeline.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
}

function Render-Ch3Protocol {
    param([string]$OutDir)
    $canvas = New-Canvas 2300 1600
    $bmp = $canvas.Bitmap
    $g = $canvas.Graphics

    Draw-Header $g 180 50 1940 110 'Locked Threshold-Transfer Evaluation Protocol' '#DBEAFE'

    Draw-Box -Graphics $g -X 760 -Y 200 -Width 780 -Height 170 -Text "Select final run`nweek7 norm only" -Fill '#EEF2FF' -FontSize 22 -MinFontSize 16 -FontStyle Bold
    Draw-Arrow -Graphics $g -X1 1150 -Y1 370 -X2 1150 -Y2 460

    Draw-Box -Graphics $g -X 610 -Y 460 -Width 1080 -Height 210 -Text "Validation only`n6106 rows`nlearn tau at 1% FPR" -Fill '#ECFCCB' -FontSize 24 -MinFontSize 16 -FontStyle Bold
    Draw-Box -Graphics $g -X 1700 -Y 490 -Width 420 -Height 150 -Text "Frozen tau" -Fill '#FEF3C7' -Stroke '#A16207' -FontSize 20 -MinFontSize 16 -FontStyle Bold

    Draw-Arrow -Graphics $g -X1 850 -Y1 670 -X2 500 -Y2 840 -Label 'fixed transfer' -LabelX 660 -LabelY 735
    Draw-Arrow -Graphics $g -X1 1450 -Y1 670 -X2 1800 -Y2 840 -Label 'fixed transfer' -LabelX 1640 -LabelY 735
    Draw-Arrow -Graphics $g -X1 1150 -Y1 670 -X2 1150 -Y2 840

    Draw-Box -Graphics $g -X 120 -Y 840 -Width 700 -Height 290 -Text "Main family`ntest_main`nplus variants" -Fill '#E0F2FE' -FontSize 24 -MinFontSize 16 -FontStyle Bold
    Draw-Box -Graphics $g -X 800 -Y 840 -Width 700 -Height 290 -Text "Report metrics`nAUROC AUPRC`nTPR FPR ASR" -Fill '#FCE7F3' -FontSize 24 -MinFontSize 16 -FontStyle Bold
    Draw-Box -Graphics $g -X 1480 -Y 840 -Width 700 -Height 290 -Text "Holdout family`ntest_jbb`nplus variants" -Fill '#EDE9FE' -FontSize 24 -MinFontSize 16 -FontStyle Bold

    Draw-Arrow -Graphics $g -X1 470 -Y1 1130 -X2 980 -Y2 1280
    Draw-Arrow -Graphics $g -X1 1150 -Y1 1130 -X2 1150 -Y2 1280
    Draw-Arrow -Graphics $g -X1 1830 -Y1 1130 -X2 1320 -Y2 1280

    Draw-Box -Graphics $g -X 560 -Y 1280 -Width 1180 -Height 190 -Text "Locked pack`nmetrics, figures, cases, config, env" -Fill '#E2E8F0' -FontSize 24 -MinFontSize 16 -FontStyle Bold

    $bmp.Save((Join-Path $OutDir 'ch3_eval_protocol.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
}

function Render-Ch6Component {
    param([string]$OutDir)
    $canvas = New-Canvas 3000 2000
    $bmp = $canvas.Bitmap
    $g = $canvas.Graphics

    Draw-Header $g 70 40 2860 110 'Shipped Runtime and Offline Evaluation Architecture' '#DCEAF5'
    Draw-Header $g 100 170 560 95 'Config and Data Sources' '#F8FAFC'
    Draw-Header $g 720 170 2200 95 'Runtime Inference Path' '#ECFCCB'
    Draw-Header $g 100 1100 2820 95 'Training, Evaluation, and Evidence Path' '#FCE7F3'

    Draw-Box -Graphics $g -X 100 -Y 300 -Width 560 -Height 185 -Text 'Data splits' -Fill '#F8FAFC' -FontSize 24 -MinFontSize 16 -FontStyle Bold
    Draw-Box -Graphics $g -X 100 -Y 530 -Width 560 -Height 185 -Text 'Run config' -Fill '#F8FAFC' -FontSize 24 -MinFontSize 16 -FontStyle Bold
    Draw-Box -Graphics $g -X 100 -Y 760 -Width 560 -Height 185 -Text 'Model artifacts' -Fill '#F8FAFC' -FontSize 24 -MinFontSize 16 -FontStyle Bold

    $runtimeY = 340
    $runtimeW = 265; $runtimeH = 240
    $runtimeXs = @(760, 1055, 1350, 1645, 1940, 2235, 2530)
    $runtimeTexts = @('CLI', 'I/O', 'Clean', 'Route', 'Rules', 'LoRA', 'Result')
    $runtimeFills = @('#EEF2FF','#E0F2FE','#ECFCCB','#FEF3C7','#FFF7ED','#EDE9FE','#E2E8F0')
    for ($i = 0; $i -lt $runtimeXs.Count; $i++) {
        Draw-Box -Graphics $g -X $runtimeXs[$i] -Y $runtimeY -Width $runtimeW -Height $runtimeH -Text $runtimeTexts[$i] -Fill $runtimeFills[$i] -FontSize 20 -MinFontSize 16 -FontStyle Bold
    }
    for ($i = 0; $i -lt $runtimeXs.Count - 1; $i++) {
        Draw-Arrow -Graphics $g -X1 ($runtimeXs[$i] + $runtimeW) -Y1 ($runtimeY + $runtimeH / 2) -X2 $runtimeXs[$i + 1] -Y2 ($runtimeY + $runtimeH / 2)
    }
    Draw-Arrow -Graphics $g -X1 660 -Y1 392 -X2 760 -Y2 392
    Draw-Arrow -Graphics $g -X1 660 -Y1 622 -X2 1645 -Y2 460
    Draw-Arrow -Graphics $g -X1 660 -Y1 852 -X2 2235 -Y2 460

    Draw-Box -Graphics $g -X 2120 -Y 650 -Width 600 -Height 170 -Text "CLI-first shipped`nno service layer delivered" -Fill '#FFFBEB' -Stroke '#A16207' -FontSize 22 -MinFontSize 15 -FontStyle Bold
    Draw-Arrow -Graphics $g -X1 2420 -Y1 650 -X2 2420 -Y2 580 -Dashed -Color '#A16207'

    $evalY = 1260
    $evalXs = @(120, 700, 1280, 1860, 2440)
    $evalW = 440; $evalH = 250
    $evalTexts = @('Training', 'Split eval', 'Grid eval', 'Tables + cases', 'Locked pack')
    $evalFills = @('#FCE7F3','#F5F3FF','#E0F2FE','#ECFCCB','#E2E8F0')
    for ($i = 0; $i -lt $evalXs.Count; $i++) {
        Draw-Box -Graphics $g -X $evalXs[$i] -Y $evalY -Width $evalW -Height $evalH -Text $evalTexts[$i] -Fill $evalFills[$i] -FontSize 24 -MinFontSize 16 -FontStyle Bold
    }
    for ($i = 0; $i -lt $evalXs.Count - 1; $i++) {
        Draw-Arrow -Graphics $g -X1 ($evalXs[$i] + $evalW) -Y1 ($evalY + $evalH / 2) -X2 $evalXs[$i + 1] -Y2 ($evalY + $evalH / 2)
    }
    Draw-Arrow -Graphics $g -X1 380 -Y1 945 -X2 380 -Y2 1260
    Draw-Arrow -Graphics $g -X1 380 -Y1 715 -X2 380 -Y2 1260
    Draw-Arrow -Graphics $g -X1 380 -Y1 485 -X2 380 -Y2 1260

    Draw-Box -Graphics $g -X 980 -Y 1620 -Width 1040 -Height 190 -Text "Frozen thesis evidence`ncounts, thresholds, metrics from the locked pack" -Fill '#DBEAFE' -FontSize 25 -MinFontSize 16 -FontStyle Bold

    $bmp.Save((Join-Path $OutDir 'ch6_component_diagram.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
}

Save-Diagram -Renderer ${function:Render-Ch3Pipeline}
Save-Diagram -Renderer ${function:Render-Ch3Protocol}
Save-Diagram -Renderer ${function:Render-Ch6Component}

if (Test-Path 'thesis_final_tex\figures\_tmp_draw_test.png') {
    Remove-Item 'thesis_final_tex\figures\_tmp_draw_test.png' -Force
}

Write-Output 'Rendered thesis diagrams.'




