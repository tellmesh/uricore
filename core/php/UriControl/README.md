# UriControl PHP placeholder

This folder is reserved for a thin PHP SDK/runner.

Target shape:

```php
$runtime->call('cms://wordpress/post/create', ['title' => 'Hello'], ['approved' => true]);
```

Keep the PHP implementation compatible with the same manifest and protobuf envelope used by Python.
