//
//  AppDelegate.swift
//  NoteTaker
//
//  Created by Gareth Jones  on 6/1/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

import UIKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?


    func application(application: UIApplication, didFinishLaunchingWithOptions launchOptions: [NSObject: AnyObject]?) -> Bool {
        // Override point for customization after application launch.
        
        // MARK: Set Status Bar to White
        UIApplication.sharedApplication().setStatusBarStyle(UIStatusBarStyle.LightContent, animated: true)
        return true
    }



}

