# Build All Brazilian Providers

Write-Host "🚀 BUILDING ALL BRAZILIAN PROVIDERS" -ForegroundColor Cyan
Write-Host "="*60

$providers = @(
    "MaxSeries",
    "AnimesOnlineCC",
    "MegaFlix",
    "NetCine",
    "OverFlix",
    "PobreFlix",
    "Vizer"
)

$results = @()

foreach ($provider in $providers) {
    Write-Host "`n📦 Building $provider..." -ForegroundColor Yellow
    
    try {
        $output = & ./gradlew "${provider}:make" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $provider - SUCCESS" -ForegroundColor Green
            $results += [PSCustomObject]@{
                Provider = $provider
                Status = "✅ SUCCESS"
                File = "$provider\build\$provider.cs3"
            }
        } else {
            Write-Host "❌ $provider - FAILED" -ForegroundColor Red
            $results += [PSCustomObject]@{
                Provider = $provider
                Status = "❌ FAILED"
                File = "N/A"
            }
        }
    } catch {
        Write-Host "❌ $provider - ERROR: $_" -ForegroundColor Red
        $results += [PSCustomObject]@{
            Provider = $provider
            Status = "❌ ERROR"
            File = "N/A"
        }
    }
}

Write-Host "`n" + ("="*60)
Write-Host "📊 BUILD SUMMARY" -ForegroundColor Cyan
Write-Host ("="*60)

$results | Format-Table -AutoSize

$successCount = ($results | Where-Object { $_.Status -eq "✅ SUCCESS" }).Count
$totalCount = $results.Count

Write-Host "`n✅ Success: $successCount/$totalCount" -ForegroundColor Green

if ($successCount -eq $totalCount) {
    Write-Host "🎉 ALL PROVIDERS BUILT SUCCESSFULLY!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some providers failed to build" -ForegroundColor Yellow
}

Write-Host ""
