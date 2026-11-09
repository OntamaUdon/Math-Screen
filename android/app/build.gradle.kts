plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("org.jetbrains.kotlin.plugin.serialization")
}

// 問題データ・単元・KaTeX は、iPhone 版と同じファイルを使う（読むだけで、書き換えない）。
// ビルドのたびに ../mathscreen/Resources からコピーするので、iPhone 版と中身がずれない。
val iosResources = rootProject.file("../mathscreen/Resources")
val sharedAssetsDir = layout.buildDirectory.dir("sharedAssets")
val copySharedAssets by tasks.registering(Sync::class) {
    from(iosResources) {
        include("problems.json", "units.json", "katex/katex.min.js", "katex/katex.min.css",
            "katex/auto-render.min.js", "katex/fonts/**")
    }
    from(iosResources.resolve("Assets.xcassets/PlanLock.imageset")) {
        include("plan-lock.png")
        into("img")
    }
    into(sharedAssetsDir)
}

android {
    namespace = "com.ontamaudon.qlock"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.ontamaudon.qlock"
        minSdk = 26
        targetSdk = 36
        // Play に送るたびに増やす番号。GitHub Actions では、実行の番号を使う
        versionCode = (project.findProperty("versionCode") as String?)?.toInt() ?: 1
        versionName = "1.0"
    }

    // リリース用の署名。鍵は GitHub の Secrets から渡す（鍵がないときは、署名なしで作る）。
    val keystorePath = System.getenv("QLOCK_KEYSTORE_PATH")
    signingConfigs {
        if (keystorePath != null) {
            create("release") {
                storeFile = file(keystorePath)
                storePassword = System.getenv("QLOCK_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("QLOCK_KEY_ALIAS")
                keyPassword = System.getenv("QLOCK_KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            if (keystorePath != null) signingConfig = signingConfigs.getByName("release")
        }
    }

    sourceSets["main"].assets.srcDir(sharedAssetsDir)

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    lint {
        abortOnError = false
        xmlReport = true
    }
    androidResources {
        noCompress += listOf("json")
    }
}

tasks.named("preBuild") { dependsOn(copySharedAssets) }
afterEvaluate {
    tasks.matching { it.name.startsWith("merge") && it.name.endsWith("Assets") }.configureEach { dependsOn(copySharedAssets) }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2025.06.00")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.activity:activity-compose:1.10.1")
    // 権限を求める処理（registerForActivityResult）が正しく動くよう、新しい Fragment を使う（lint の指摘）
    implementation("androidx.fragment:fragment-ktx:1.8.6")
    implementation("androidx.core:core-ktx:1.16.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.1")
    implementation("androidx.webkit:webkit:1.14.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")
    implementation("com.android.billingclient:billing-ktx:8.0.0")
    debugImplementation("androidx.compose.ui:ui-tooling")
    testImplementation("junit:junit:4.13.2")
}
