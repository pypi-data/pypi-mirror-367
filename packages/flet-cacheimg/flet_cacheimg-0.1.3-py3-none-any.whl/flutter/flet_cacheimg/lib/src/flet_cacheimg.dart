import 'dart:convert';
import 'dart:typed_data';
import 'dart:io' as io;

import 'package:flet/flet.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:cached_network_image/cached_network_image.dart';

class FletCacheImgControl extends StatelessWidget with FletStoreMixin {
  final Control? parent;
  final List<Control> children;
  final Control control;
  final bool parentDisabled;
  final bool? parentAdaptive;
  final FletControlBackend backend;

  static const String svgTag = " xmlns=\"http://www.w3.org/2000/svg\"";

  const FletCacheImgControl({
    super.key,
    required this.parent,
    required this.children,
    required this.control,
    required this.parentDisabled,
    required this.parentAdaptive,
    required this.backend,
  });

  @override
  Widget build(BuildContext context) {
    debugPrint("Image build: ${control.id}");
    bool disabled = control.isDisabled || parentDisabled;

    var src = control.attrString("src", "")!;
    var srcBase64 = control.attrString("srcBase64", "")!;
    if (src == "" && srcBase64 == "") {
      return const ErrorControl(
          "Image must have either \"src\" or \"src_base64\" specified.");
    }

    var errorContentCtrls =
        children.where((c) => c.name == "error_content" && c.isVisible);

    return withPageArgs((context, pageArgs) {
      Widget? image = buildCachedImage(
        context: context,
        control: control,
        src: src,
        srcBase64: srcBase64,
        width: control.attrDouble("width"),
        height: control.attrDouble("height"),
        cacheWidth: control.attrInt("cacheWidth"),
        cacheHeight: control.attrInt("cacheHeight"),
        antiAlias: control.attrBool("antiAlias", false)!,
        repeat: parseImageRepeat(
            control.attrString("repeat"), ImageRepeat.noRepeat)!,
        fit: parseBoxFit(control.attrString("fit")),
        colorBlendMode: parseBlendMode(control.attrString("colorBlendMode")),
        color: control.attrColor("color", context),
        semanticsLabel: control.attrString("semanticsLabel"),
        gaplessPlayback: control.attrBool("gaplessPlayback"),
        excludeFromSemantics: control.attrBool("excludeFromSemantics", false)!,
        filterQuality: parseFilterQuality(
            control.attrString("filterQuality"), FilterQuality.medium)!,
        disabled: disabled,
        pageArgs: pageArgs,
        errorCtrl: errorContentCtrls.isNotEmpty
            ? createControl(control, errorContentCtrls.first.id, disabled,
                parentAdaptive: control.isAdaptive ?? parentAdaptive)
            : null,
      );

      return constrainedControl(
        context,
        _clipCorners(image, control),
        parent,
        control,
      );
    });
  }

  Widget _clipCorners(Widget image, Control control) {
    var borderRadius = parseBorderRadius(control, "borderRadius");
    return borderRadius != null
        ? ClipRRect(borderRadius: borderRadius, child: image)
        : image;
  }
}

Widget buildCachedImage({
  required BuildContext context,
  required Control control,
  required Widget? errorCtrl,
  required String? src,
  required String? srcBase64,
  double? width,
  double? height,
  ImageRepeat repeat = ImageRepeat.noRepeat,
  BoxFit? fit,
  BlendMode? colorBlendMode,
  Color? color,
  String? semanticsLabel,
  bool? gaplessPlayback,
  int? cacheWidth,
  int? cacheHeight,
  bool antiAlias = false,
  bool excludeFromSemantics = false,
  FilterQuality filterQuality = FilterQuality.low,
  bool disabled = false,
  required PageArgsModel pageArgs,
}) {
  const String svgTag = " xmlns=\"http://www.w3.org/2000/svg\"";
  Widget? image;

  if (srcBase64 != null && srcBase64.isNotEmpty) {
    try {
      Uint8List bytes = base64Decode(srcBase64);
      if (arrayIndexOf(bytes, Uint8List.fromList(utf8.encode(svgTag))) != -1) {
        image = SvgPicture.memory(
          bytes,
          width: width,
          height: height,
          fit: fit ?? BoxFit.contain,
          colorFilter: color != null
              ? ColorFilter.mode(color, colorBlendMode ?? BlendMode.srcIn)
              : null,
          semanticsLabel: semanticsLabel,
        );
      } else {
        image = Image.memory(
          bytes,
          width: width,
          height: height,
          repeat: repeat,
          fit: fit,
          color: color,
          cacheHeight: cacheHeight,
          cacheWidth: cacheWidth,
          filterQuality: filterQuality,
          isAntiAlias: antiAlias,
          colorBlendMode: colorBlendMode,
          gaplessPlayback: gaplessPlayback ?? true,
          semanticLabel: semanticsLabel,
        );
      }
      return image;
    } catch (ex) {
      return ErrorControl("Error decoding base64: ${ex.toString()}");
    }
  } else if (src != null && src.isNotEmpty) {
    if (src.contains(svgTag)) {
      image = SvgPicture.memory(
        Uint8List.fromList(utf8.encode(src)),
        width: width,
        height: height,
        fit: fit ?? BoxFit.contain,
        colorFilter: color != null
            ? ColorFilter.mode(color, colorBlendMode ?? BlendMode.srcIn)
            : null,
        semanticsLabel: semanticsLabel,
      );
    } else {
      final assetSrc = getAssetSrc(src, pageArgs.pageUri!, pageArgs.assetsDir);

      if (assetSrc.isFile) {
        if (assetSrc.path.endsWith(".svg")) {
          image = getSvgPictureFromFile(
            src: assetSrc.path,
            width: width,
            height: height,
            fit: fit ?? BoxFit.contain,
            color: color,
            blendMode: colorBlendMode ?? BlendMode.srcIn,
            semanticsLabel: semanticsLabel,
          );
        } else {
          image = Image.file(
            io.File(assetSrc.path),
            width: width,
            height: height,
            repeat: repeat,
            filterQuality: filterQuality,
            excludeFromSemantics: excludeFromSemantics,
            fit: fit,
            color: color,
            isAntiAlias: antiAlias,
            cacheHeight: cacheHeight,
            cacheWidth: cacheWidth,
            gaplessPlayback: gaplessPlayback ?? false,
            colorBlendMode: colorBlendMode,
            semanticLabel: semanticsLabel,
            errorBuilder: errorCtrl != null
                ? (context, error, stackTrace) => errorCtrl
                : null,
          );
        }
      } else {
        if (assetSrc.path.endsWith(".svg")) {
          image = SvgPicture.network(
            assetSrc.path,
            width: width,
            height: height,
            excludeFromSemantics: excludeFromSemantics,
            fit: fit ?? BoxFit.contain,
            colorFilter: color != null
                ? ColorFilter.mode(color, colorBlendMode ?? BlendMode.srcIn)
                : null,
            semanticsLabel: semanticsLabel,
          );
        } else {
          image = CachedNetworkImage(
            imageUrl: assetSrc.path,
            width: width,
            height: height,
            fit: fit,
            repeat: repeat,
            filterQuality: filterQuality,
            color: color,
            colorBlendMode: colorBlendMode,
            errorWidget: errorCtrl != null
                ? (context, url, error) => errorCtrl!
                : (context, url, error) => const Icon(Icons.error),
          );
        }
      }
    }
    return image;
  }

  return const ErrorControl("A valid src or src_base64 must be specified.");
}
