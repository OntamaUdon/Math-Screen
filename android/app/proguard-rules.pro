# 保存データ（kotlinx.serialization）のクラスを残す
-keepattributes *Annotation*, InnerClasses
-keep,includedescriptorclasses class com.ontamaudon.qlock.**$$serializer { *; }
-keepclassmembers class com.ontamaudon.qlock.** { *** Companion; }
-keepclasseswithmembers class com.ontamaudon.qlock.** { kotlinx.serialization.KSerializer serializer(...); }
# KaTeX の WebView から呼ぶ関数
-keepclassmembers class * { @android.webkit.JavascriptInterface <methods>; }
