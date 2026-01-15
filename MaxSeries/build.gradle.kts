plugins {
    id("com.android.library")
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "com.franciscoalro.maxseries"
    
    compileSdk = libs.versions.compileSdk.get().toInt()
    
    defaultConfig {
        minSdk = libs.versions.minSdk.get().toInt()
        targetSdk = libs.versions.targetSdk.get().toInt()
        
        // Plugin metadata
        buildConfigField("String", "PLUGIN_NAME", "\"MaxSeries\"")
        buildConfigField("String", "PLUGIN_VERSION", "\"80\"")
        buildConfigField("String", "PLUGIN_DESCRIPTION", "\"MaxSeries v80 - Cloudstream Pre-Release Compatible (Jan 2026)\"")
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = "1.8"
        freeCompilerArgs += listOf(
            "-opt-in=com.lagradost.cloudstream3.Prerelease"
        )
    }
    
    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    // Cloudstream Library (local project)
    implementation(project(":library"))
    
    // Core Dependencies
    implementation(libs.core.ktx)
    implementation(libs.appcompat)
    
    // Networking
    implementation(libs.nicehttp)
    implementation(libs.jackson.module.kotlin)
    implementation(libs.jsoup)
    
    // Coroutines
    implementation(libs.kotlinx.coroutines.core)
    
    // WebView (for extractors)
    implementation("androidx.webkit:webkit:1.8.0")
}
