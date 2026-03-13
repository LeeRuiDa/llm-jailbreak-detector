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

function Draw-FittedText {
    param(
        $Graphics,
        [string]$Text,
        [System.Drawing.RectangleF]$Rect,
        [int]$MaxFontSize = 26,
        [int]$MinFontSize = 14,
        [string]$FontStyle = 'Regular',
        [string]$Color = '#111827'
    )
    $style = [System.Drawing.FontStyle]::$FontStyle
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $format.Trimming = [System.Drawing.StringTrimming]::Word
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
        [int]$FontSize = 24,
        [int]$MinFontSize = 14,
        [string]$FontStyle = 'Regular',
        [float]$Radius = 20,
        [int]$Padding = 16
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

function Draw-LineArrow {
    param(
        $Graphics,
        [float]$X1,
        [float]$Y1,
        [float]$X2,
        [float]$Y2,
        [string]$Color = '#475569',
        [float]$Width = 4,
        [switch]$Dashed
    )
    $pen = New-Object System.Drawing.Pen (Get-Color $Color), $Width
    if ($Dashed) { $pen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash }
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap 6, 8, $true
    $pen.CustomEndCap = $cap
    $Graphics.DrawLine($pen, $X1, $Y1, $X2, $Y2)
    $cap.Dispose(); $pen.Dispose()
}

function Draw-Lifeline {
    param($Graphics,[float]$X,[float]$Y1,[float]$Y2,[string]$Color='#94A3B8')
    $pen = New-Object System.Drawing.Pen (Get-Color $Color), 3
    $pen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
    $Graphics.DrawLine($pen, $X, $Y1, $X, $Y2)
    $pen.Dispose()
}

function Draw-Label {
    param($Graphics,[float]$X,[float]$Y,[float]$W,[float]$H,[string]$Text,[int]$FontSize=18,[string]$FontStyle='Regular')
    $rect = [System.Drawing.RectangleF]::new($X,$Y,$W,$H)
    Draw-FittedText -Graphics $Graphics -Text $Text -Rect $rect -MaxFontSize $FontSize -MinFontSize 12 -FontStyle $FontStyle -Color '#334155'
}

$targets = @('docs/figures','thesis_final_tex/figures')
foreach ($outDir in $targets) {
    $canvas = New-Canvas 2800 1800
    $bmp = $canvas.Bitmap
    $g = $canvas.Graphics

    Draw-Box -Graphics $g -X 80 -Y 40 -Width 2640 -Height 100 -Text 'Prediction Flow for jbd predict' -Fill '#DBEAFE' -Stroke '#0F172A' -FontSize 26 -FontStyle Bold

    $lanes = @(
        @{x=220; label='CLI'; fill='#EEF2FF'},
        @{x=760; label='Normalize'; fill='#ECFCCB'},
        @{x=1300; label='Predictor'; fill='#FEF3C7'},
        @{x=1840; label='Backend'; fill='#F5F3FF'},
        @{x=2380; label='Output'; fill='#E2E8F0'}
    )

    foreach ($lane in $lanes) {
        Draw-Box -Graphics $g -X ($lane.x - 160) -Y 180 -Width 320 -Height 100 -Text $lane.label -Fill $lane.fill -FontSize 24 -FontStyle Bold
        Draw-Lifeline -Graphics $g -X $lane.x -Y1 290 -Y2 1600
    }

    $steps = @(
        @{y=370; from=220; to=1300; label='build Predictor'},
        @{y=500; from=1300; to=1300; label='resolve threshold'},
        @{y=670; from=220; to=760; label='optional normalize'},
        @{y=800; from=760; to=1300; label='return normalized text'},
        @{y=950; from=1300; to=1840; label='select backend'},
        @{y=1110; from=1840; to=1840; label='rules or LoRA'},
        @{y=1270; from=1840; to=1300; label='return score'},
        @{y=1430; from=1300; to=1300; label='apply threshold'},
        @{y=1560; from=1300; to=2380; label='emit JSON result'}
    )

    foreach ($s in $steps) {
        if ($s.from -eq $s.to) {
            Draw-Box -Graphics $g -X ($s.from - 185) -Y ($s.y - 35) -Width 370 -Height 70 -Text $s.label -Fill '#FFFFFF' -Stroke '#94A3B8' -FontSize 16 -MinFontSize 12 -Radius 14
        } else {
            Draw-LineArrow -Graphics $g -X1 $s.from -Y1 $s.y -X2 $s.to -Y2 $s.y
            $left = [Math]::Min($s.from,$s.to)
            $width = [Math]::Abs($s.to - $s.from)
            Draw-Label -Graphics $g -X ($left + 20) -Y ($s.y - 44) -W ($width - 40) -H 34 -Text $s.label -FontSize 16
        }
    }

    Draw-Box -Graphics $g -X 1740 -Y 1185 -Width 200 -Height 65 -Text 'rules' -Fill '#FFF7ED' -Stroke '#9A3412' -FontSize 18 -FontStyle Bold -Radius 14
    Draw-Box -Graphics $g -X 1955 -Y 1185 -Width 200 -Height 65 -Text 'local LoRA' -Fill '#EDE9FE' -Stroke '#6D28D9' -FontSize 18 -FontStyle Bold -Radius 14
    Draw-Box -Graphics $g -X 140 -Y 1660 -Width 2520 -Height 85 -Text 'Design intent: minimal CLI, centralized thresholding, optional normalization, local-only LoRA.' -Fill '#F8FAFC' -Stroke '#475569' -FontSize 20 -MinFontSize 14

    $bmp.Save((Join-Path $outDir 'ch6_prediction_sequence.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
}
Write-Output 'Rendered ch6 prediction sequence.'
