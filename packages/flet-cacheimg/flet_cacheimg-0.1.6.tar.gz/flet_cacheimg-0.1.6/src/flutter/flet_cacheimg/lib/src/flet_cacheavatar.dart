import 'dart:convert';
import 'dart:typed_data';
import 'dart:io' as io;

import 'package:flet/flet.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:cached_network_image/cached_network_image.dart';

class FletCacheCircleAvatarControl extends StatelessWidget with FletStoreMixin {
  final Control? parent;
  final Control control;
  final List<Control> children;
  final bool parentDisabled;
  final FletControlBackend backend;

  const FletCacheCircleAvatarControl(
      {super.key,
      this.parent,
      required this.control,
      required this.children,
      required this.parentDisabled,
      required this.backend});

  @override
  Widget build(BuildContext context) {
    debugPrint("CircleAvatar build: ${control.id}");
    bool disabled = control.isDisabled || parentDisabled;

    return withPageArgs((context, pageArgs) {
      var foregroundImageSrc = control.attrString("foregroundImageSrc");
      var backgroundImageSrc = control.attrString("backgroundImageSrc");
      var contentCtrls =
          children.where((c) => c.name == "content" && c.isVisible);

      ImageProvider<Object>? backgroundImage;
      ImageProvider<Object>? foregroundImage;

      if (foregroundImageSrc != null || backgroundImageSrc != null) {
        var assetSrc = getAssetSrc((foregroundImageSrc ?? backgroundImageSrc)!,
            pageArgs.pageUri!, pageArgs.assetsDir);

        // foregroundImage
        if (foregroundImageSrc != null) {
          if (assetSrc.isFile) {
            // from File
            foregroundImage = AssetImage(assetSrc.path);
          } else {
            // URL
            foregroundImage = CachedNetworkImageProvider(assetSrc.path);
          }
        }

        // backgroundImage
        if (backgroundImageSrc != null) {
          if (assetSrc.isFile) {
            // from File
            backgroundImage = AssetImage(assetSrc.path);
          } else {
            // URL
            backgroundImage = CachedNetworkImageProvider(assetSrc.path);
          }
        }
      }

      var avatar = CircleAvatar(
          foregroundImage: foregroundImage,
          backgroundImage: backgroundImage,
          backgroundColor: control.attrColor("bgColor", context),
          foregroundColor: control.attrColor("color", context),
          radius: control.attrDouble("radius"),
          minRadius: control.attrDouble("minRadius"),
          maxRadius: control.attrDouble("maxRadius"),
          onBackgroundImageError: backgroundImage != null
              ? (object, trace) {
                  backend.triggerControlEvent(
                      control.id, "imageError", "background");
                }
              : null,
          onForegroundImageError: foregroundImage != null
              ? (object, trace) {
                  backend.triggerControlEvent(
                      control.id, "imageError", "foreground");
                }
              : null,
          child: contentCtrls.isNotEmpty
              ? createControl(control, contentCtrls.first.id, disabled)
              : null);

      return constrainedControl(context, avatar, parent, control);
    });
  }
}