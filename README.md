# LED 燈條

### install demo.service

```bash
sudo cp demo.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable demo.service
sudo systemctl start demo.service
```

### stop demo.service

```bash
sudo systemctl stop demo.service
```
