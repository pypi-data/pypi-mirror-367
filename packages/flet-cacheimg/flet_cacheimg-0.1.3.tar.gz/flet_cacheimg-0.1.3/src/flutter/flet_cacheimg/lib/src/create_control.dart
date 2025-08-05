import 'package:flet/flet.dart';
import 'package:flet_cacheimg/src/flet_cacheimg.dart';
import 'package:flet_cacheimg/src/flet_cacheavatar.dart';

CreateControlFactory createControl = (CreateControlArgs args) {
  final type = args.control.type.trim().toLowerCase();
  print("createControl called with type: '$type'");

    if (type == "flet_cacheimg") {
        print("return FletCacheImgControl");
        return FletCacheImgControl(
          key: args.key,
          parent: args.parent,
          children: args.children,
          control: args.control,
          parentDisabled: args.parentDisabled,
          parentAdaptive: args.parentAdaptive,
          backend: args.backend,
        );
    }

    if (type == "flet_cache_circle_avatar") {
      print("return FletCacheCircleAvatarControl");
      return FletCacheCircleAvatarControl(
        key: args.key,
        parent: args.parent,
        children: args.children,
        control: args.control,
        parentDisabled: args.parentDisabled,
        backend: args.backend,
      );
  }

  print("No matching control for type: '$type', returning null");
  return null;
};

void ensureInitialized() {
  print("flet_cacheimg.ensureInitialized called");
}
