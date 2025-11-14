# ============================================================================
# MinIO Image Upload Test - Social Media Posts
# ============================================================================

$baseUrl = "http://localhost:8000/api/posts/"

Write-Host "`n=== MinIO IMAGE UPLOAD TEST ===" -ForegroundColor Green

# Erstelle ein Test-Bild (1x1 Pixel PNG)
$testImagePath = "$env:TEMP\test-post-image.png"

# Base64 encoded 1x1 transparent PNG
$base64Png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
$bytes = [Convert]::FromBase64String($base64Png)
[IO.File]::WriteAllBytes($testImagePath, $bytes)

Write-Host "`nTest image created at: $testImagePath" -ForegroundColor Yellow

# ============================================================================
# 1. POST mit Bild-Upload (multipart/form-data)
# ============================================================================

Write-Host "`n`n=== 1. CREATE POST WITH IMAGE UPLOAD ===" -ForegroundColor Green

$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

# Multipart Form Data manuell erstellen
$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"user`"$LF",
    "1",
    "--$boundary",
    "Content-Disposition: form-data; name=`"title`"$LF",
    "Post with MinIO Image Upload",
    "--$boundary",
    "Content-Disposition: form-data; name=`"text`"$LF",
    "This post includes an image stored in MinIO object storage",
    "--$boundary",
    "Content-Disposition: form-data; name=`"image_file`"; filename=`"test-image.png`"",
    "Content-Type: image/png$LF",
    [System.Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($testImagePath)),
    "--$boundary--$LF"
)

$body = $bodyLines -join $LF

try {
    Write-Host "Uploading post with image..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri $baseUrl `
        -Method POST `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $body
    
    Write-Host "✅ Success! Response:" -ForegroundColor Green
    $responseData = $response.Content | ConvertFrom-Json
    Write-Host ($responseData | ConvertTo-Json -Depth 3) -ForegroundColor Cyan
    
    $postId = $responseData.id
    $imagePath = $responseData.image
    
    Write-Host "`nPost ID: $postId" -ForegroundColor Magenta
    Write-Host "Image Path in MinIO: $imagePath" -ForegroundColor Magenta
    
    # ============================================================================
    # 2. GET Post und prüfe Image-URL
    # ============================================================================
    
    Write-Host "`n`n=== 2. RETRIEVE POST AND CHECK IMAGE ===" -ForegroundColor Green
    
    $getResponse = Invoke-WebRequest -Uri "$baseUrl$postId/"
    $postData = $getResponse.Content | ConvertFrom-Json
    
    Write-Host "Retrieved Post:" -ForegroundColor Yellow
    Write-Host ($postData | ConvertTo-Json -Depth 3) -ForegroundColor Cyan
    
    # ============================================================================
    # 3. UPDATE Post mit neuem Bild
    # ============================================================================
    
    Write-Host "`n`n=== 3. UPDATE POST WITH NEW IMAGE ===" -ForegroundColor Green
    
    $updateBoundary = [System.Guid]::NewGuid().ToString()
    $updateBodyLines = @(
        "--$updateBoundary",
        "Content-Disposition: form-data; name=`"user`"$LF",
        "1",
        "--$updateBoundary",
        "Content-Disposition: form-data; name=`"title`"$LF",
        "UPDATED - Post with New Image",
        "--$updateBoundary",
        "Content-Disposition: form-data; name=`"text`"$LF",
        "Updated post with a new image in MinIO",
        "--$updateBoundary",
        "Content-Disposition: form-data; name=`"image_file`"; filename=`"test-image-updated.png`"",
        "Content-Type: image/png$LF",
        [System.Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($testImagePath)),
        "--$updateBoundary--$LF"
    )
    
    $updateBody = $updateBodyLines -join $LF
    
    Write-Host "Updating post with new image..." -ForegroundColor Yellow
    $updateResponse = Invoke-WebRequest -Uri "$baseUrl$postId/" `
        -Method PUT `
        -ContentType "multipart/form-data; boundary=$updateBoundary" `
        -Body $updateBody
    
    Write-Host "✅ Updated! Response:" -ForegroundColor Green
    $updatedData = $updateResponse.Content | ConvertFrom-Json
    Write-Host ($updatedData | ConvertTo-Json -Depth 3) -ForegroundColor Cyan
    
    Write-Host "`nOld Image Path: $imagePath" -ForegroundColor Yellow
    Write-Host "New Image Path: $($updatedData.image)" -ForegroundColor Green
    
    # ============================================================================
    # 4. Erstelle Post OHNE Bild
    # ============================================================================
    
    Write-Host "`n`n=== 4. CREATE POST WITHOUT IMAGE ===" -ForegroundColor Green
    
    $noImageBody = @{
        user = 2
        title = "Post without Image"
        text = "This post has no image"
    } | ConvertTo-Json
    
    $noImageResponse = Invoke-WebRequest -Uri $baseUrl `
        -Method POST `
        -ContentType "application/json" `
        -Body $noImageBody
    
    Write-Host "✅ Created post without image:" -ForegroundColor Green
    Write-Host $noImageResponse.Content -ForegroundColor Cyan
    
    # ============================================================================
    # 5. Liste alle Posts
    # ============================================================================
    
    Write-Host "`n`n=== 5. LIST ALL POSTS ===" -ForegroundColor Green
    
    $allPosts = Invoke-WebRequest -Uri $baseUrl
    Write-Host $allPosts.Content -ForegroundColor Cyan
    
    # ============================================================================
    # 6. Lösche Post (sollte auch Bild aus MinIO löschen)
    # ============================================================================
    
    Write-Host "`n`n=== 6. DELETE POST (and image from MinIO) ===" -ForegroundColor Green
    
    Write-Host "Deleting post $postId..." -ForegroundColor Yellow
    $deleteResponse = Invoke-WebRequest -Uri "$baseUrl$postId/" -Method DELETE
    
    Write-Host "✅ Post deleted! Status: $($deleteResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Image should also be removed from MinIO storage" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Error occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}

# Cleanup
Remove-Item $testImagePath -ErrorAction SilentlyContinue

Write-Host "`n`n=== TEST COMPLETE ===" -ForegroundColor Green
Write-Host "Check MinIO Console at: http://localhost:9001/" -ForegroundColor Magenta
Write-Host "Login: minio / mino_admin" -ForegroundColor Magenta
Write-Host "Bucket: social-media-bucket" -ForegroundColor Magenta
