import com.android.build.gradle.BaseExtension
import com.lagradost.cloudstream3.gradle.CloudstreamExtension
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.tasks.KotlinJvmCompile

buildscript {
    repositories {
        google()
        mavenCentral()
        maven("https://jitpack.io")
    }

    dependencies {
        classpath("com.android.tools.build:gradle:8.13.2")
        classpath("com.github.recloudstream:gradle:cce1b8d84d") {
            exclude(group = "com.github.vidstige", module = "jadb")
        }
        classpath("com.github.vidstige:jadb:v1.2.1")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.3.0")
        classpath("org.jetbrains.kotlin:kotlin-serialization:2.3.0")
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
        maven("https://jitpack.io")
    }
    
    configurations.all {
        resolutionStrategy {
            force("org.jetbrains.kotlin:kotlin-stdlib:2.3.0")
            force("org.jetbrains.kotlin:kotlin-stdlib-jdk8:2.3.0")
            force("org.jetbrains.kotlin:kotlin-stdlib-jdk7:2.3.0")
            force("org.jetbrains.kotlin:kotlin-stdlib-common:2.3.0")
            force("org.jetbrains.kotlin:kotlin-reflect:2.3.0")
        }
    }
}

fun Project.cloudstream(configuration: CloudstreamExtension.() -> Unit) = extensions.getByName<CloudstreamExtension>("cloudstream").configuration()

fun Project.android(configuration: BaseExtension.() -> Unit) = extensions.getByName<BaseExtension>("android").configuration()

subprojects {
    apply(plugin = "com.android.library")
    apply(plugin = "kotlin-android")
    apply(plugin = "kotlinx-serialization")
    apply(plugin = "com.lagradost.cloudstream3.gradle")

    cloudstream {
        setRepo(System.getenv("GITHUB_REPOSITORY") ?: "franciscoalro/TestPlugins")
    }

    android {
        namespace = "com.recloudstream"
        defaultConfig {
            minSdk = 21
            compileSdkVersion(35)
            targetSdk = 35
        }

        compileOptions {
            sourceCompatibility = JavaVersion.VERSION_1_8
            targetCompatibility = JavaVersion.VERSION_1_8
        }

        tasks.withType<KotlinJvmCompile> {
            compilerOptions {
                jvmTarget.set(JvmTarget.JVM_1_8)
                freeCompilerArgs.addAll(
                    "-Xno-call-assertions",
                    "-Xno-param-assertions",
                    "-Xno-receiver-assertions"
                )
            }
        }
    }

    dependencies {
        val implementation by configurations

        implementation("com.github.recloudstream.cloudstream:library:8a4480dc42") // Commit hash estável (fix JitPack)
        implementation(kotlin("stdlib", "2.3.0"))
        implementation("com.github.Blatzar:NiceHttp:0.4.13")
        implementation("org.jsoup:jsoup:1.19.1")
        implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.16.0")
        implementation("com.fasterxml.jackson.core:jackson-databind:2.16.0")
        implementation("com.squareup.okhttp3:okhttp:4.12.0")
        implementation("androidx.webkit:webkit:1.8.0")
        implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.1")
        
        // Ferramentas do saimuelrepo-main
        implementation("org.mozilla:rhino:1.8.0")
        implementation("app.cash.quickjs:quickjs-android:0.9.2")
        implementation("me.xdrop:fuzzywuzzy:1.4.0")
        implementation("com.google.code.gson:gson:2.11.0")
        implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.0")
        implementation("com.github.vidstige:jadb:v1.2.1")
    }
}

task<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
