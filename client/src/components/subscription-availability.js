import React, { useEffect, useState, useRef } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Backdrop, Button, CircularProgress, Divider, FormControl, Grid, IconButton, Snackbar, TextField } from '@material-ui/core';
import { AgGridReact } from 'ag-grid-react/lib/agGridReact';
import { AgGridColumn } from 'ag-grid-react/lib/agGridColumn';
import CloseIcon from '@material-ui/icons/Close';
import { disColumns, districtColumnMap, pincodeColumnMap, pinColumns } from '../constants';

const useStyles = makeStyles((theme) => ({
    close: {
      padding: theme.spacing(0.5),
    },
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
        color: '#fff',
    },
}));

const SubscriptionAvailability = props => {
    const classes = useStyles();
    const [gridData, setGridData] = useState({
        'STDIS': [],
        'PINCD': [],
    });
    const [email, setEmail] = useState('');
    let evtSource;
    const gridRef = useRef();
    const [backdrop, setBackdrop] = useState(false);
    const [message, setMessage] = useState({
        open: false,
        msg: ''
    });
    
    
    const handleMessageClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setMessage({open: false, msg: ''});
    }

    const onEmailChange = e => {
        setEmail(e.target.value);
    }

    const evtSourceCb = (cb) => {
        try {
            return (ev) => cb(ev);
        } catch (error) {
            setMessage({
                open: true,
                msg: 'Error occurred in streaming'
            });
        }
    }

    let interval;

    const randomNum = (max, min = 0) => Math.random() * (max - min) + min;

    const streamSubscriptions = () => {
        if (interval) {
            clearInterval(interval);
        }

        interval = setInterval(async () => {
            let r = await fetch(`/api/v2/stream/subscriptions?email=${email}`);
            let res = await r.json()
            console.log('Fetching stream subscriptions')
            console.log(res);
        }, ( () => {
            let randNum = randomNum(3, 1);
            return randNum * 1000;
        } )())

        // evtSource = new EventSource(`/api/v2/stream/subscriptions?email=${email}`);


        // evtSource.onmessage = (e) => {
        //     // Do something - event data etc will be in e.data
        //     console.log('OnMessage method on eventSource')
        //     console.log(e);
        // };
    
        // evtSource.addEventListener("update", evtSourceCb(e => {
        //     console.log('stream update')
        //     console.log(e);
        // }));
        
        // evtSource.addEventListener("message", evtSourceCb(e => {
        //     console.log('stream Message')
        //     console.log(e);
        // }));
        
        // evtSource.addEventListener("end", evtSourceCb(e => {
        //     console.log('stream end')
        //     console.log(e);
        //     evtSource.close();
        // }));
    }

    useEffect(() => {
        if (!email && evtSource) {
            evtSource.close();
        }
        if (!email && interval) {
            clearInterval(interval);
        }
    }, [email]);

    useEffect(() => {
        // Unmounting component
        return () => {
            // if (evtSource) {
            //     evtSource.close();
            // }
            if (interval) {
                clearInterval(interval);
            }
        }
    }, []);



    return <>
    <Snackbar
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        open={message.open}
        autoHideDuration={6000}
        onClose={handleMessageClose}
        message={message.msg}
        action={
          <>
            <IconButton aria-label="close" color="inherit"
              className={classes.close} onClick={handleMessageClose}
            >
              <CloseIcon />
            </IconButton>
          </>
        }
    />
    <Backdrop className={classes.backdrop} open={backdrop}>
        <CircularProgress color="inherit" />
    </Backdrop>
    <Grid container item xs={12} sm={12} md={12} direction='row'>
        <Grid item xs={2} sm={2} md={2}>
            <FormControl variant="standard" style={{paddingLeft: 8}} >
                <TextField id="full-width-email"
                    placeholder="Enter your email ID"
                    fullWidth 
                    margin="normal"
                    InputLabelProps={{
                        shrink: true,
                    }}
                    variant="standard" type='email' value={email}
                    onChange={onEmailChange}
                />
            </FormControl>
        </Grid>
        <Grid item alignSelf='center'>
            <Button variant="contained" color="primary" style={{ paddingLeft: 8 }}
                onClick={streamSubscriptions}
            >
                Stream Subscriptions
            </Button>
        </Grid>
    </Grid>
    <Grid container item xs={12} sm={12} md={12} direction='row'>

        <Grid item xs={7} md={7} sm={7}>
            <div className="ag-theme-material" style={{ height: 400 }}>
                <AgGridReact ref={gridRef} rowData={gridData['STDIS']} >
                    {/* <AgGridColumn field="email" headerName='Email' sortable={ true } filter={ true }></AgGridColumn> */}
                    {
                        disColumns.map(col => <AgGridColumn field={districtColumnMap[col]} headerName={col} sortable={ true } filter={ true }></AgGridColumn>)
                    }
                </AgGridReact>
            </div>

        </Grid>
        <Divider orientation="vertical" flexItem />
        <Grid item xs={4} md={4} sm={4}>
            <div className="ag-theme-material" style={{ height: 400 }}>
                <AgGridReact ref={gridRef} rowData={gridData['PINCD']} >
                {
                        pinColumns.map(col => <AgGridColumn field={pincodeColumnMap[col]} headerName={col} sortable={ true } filter={ true }></AgGridColumn>)
                    }
                </AgGridReact>
            </div>

        </Grid>
    </Grid>
    </>
}


export default SubscriptionAvailability;