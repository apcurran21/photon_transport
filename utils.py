import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm


DEBUG = False


"""
--------------------------------------------
Utility Functions
--------------------------------------------
"""

def get_curr_time():
    # return a formatted string of the current time
    return datetime.now().strftime("%Y-%m-%d+%H-%M-%S")

def equal(a0, a1):
    # test for equality between two numpy arrays using the default tolerance of 10e-8.
    # meant for checking locations and directions.
    return np.all( np.isclose( a0, a1 ) )

def gen_xi(num_samples):
    return np.random.uniform(0, 1, num_samples)

def specular_reflectance(n_0, n_1):
    return ( ( n_0 - n_1 ) / ( n_0 + n_1 ) ) ** 2

def sample_s(m_t):
    # returns a single sample of the step size
    xi = gen_xi(1)
    return -np.log( xi ) / m_t

def sample_cos_theta(g):
    # returns a single sample of cos(theta)
    xi = gen_xi(1)
    if g == 0:
        return 2 * xi - 1
    else:
        c1 = 1 / ( 2 * g )
        c2 = ( ( 1 - g ** 2 ) / ( 1 - g + 2 * g * xi ) ) ** 2 
        c3 = 1 + g ** 2 - c2
        return c1 * c3

def sample_phi():
    # returns a single sample of the azimuthal angle
    xi = gen_xi(1)
    return 2 * np.pi * xi

def absorbance_matrix(Nz, Nr):
    # create an absorbance matrix specific to Figure 4 in Wang MCML
    return np.zeros((Nz, Nr))

def get_absorbance_loc(p, res, Nz, Nr):
    # return a tuple indicating the correct spot in the absorbance array (with shape [Nz,Nr]) for the given photon p, at the grid line separation res
    z = int( p.loc.z / res )
    r = int( np.sqrt( p.loc.x ** 2 + p.loc.y ** 2 ) / res )
    return ( min(z, Nz-1), min(r, Nr-1) )

def get_distance(p0, p1):
    # calculate the Euclidean distance between two points (z, r), represented as tuples.
    return np.sqrt( ( p0[0] - p1[0] ) ** 2 + ( p0[1] - p1[1] ) ** 2 )

def plot_fluence(results_path):
    # does a comparison of the two different n ratios (1 and 1.37) on the same plot
    # each of the photon packet numbers are split into different subplots
    # `results_path` is a Path object to the simulation run's absorbance results

    # just hardcode the specific sim params, eventually track this in json
    ma = 0.1       # [cm-1]
    # ms = 100       # [cm-1]
    # mt = ma + ms   # [cm-1]
    Nz = 200 
    # Nr = int(Nz / 3)
    # ir = np.arange(Nr)
    Dz = 0.005
    # Dr = 0.005
    # Da = 2 * np.pi * ( ir + 0.5 ) * Dr ** 2
    x = np.linspace(0, 0 + (Nz - 1) * Dz, Nz)

    photon_nums = [1000, 10000, 100000, 1000000]

    fig, axes = plt.subplots(2, 2, figsize=(8, 8))
    axes = axes.flatten()
    
    for i, num in enumerate(photon_nums):

        n_rel0 = 1.0
        n_rel1 = 1.37

        A_str0 = f"A_{num}packets_1-0n0_1-0n1-npy.npy"
        # zgb_str0 = f"zgb_{num}packets_1-0n0_1-0n1.npy"
        # rgb_str0 = f"rgb_{num}packets_1-0n0_1-0n1.npy"
        A_str1 = f"A_{num}packets_1-0n0_1-37n1-npy.npy"
        # zgb_str1 = f"zgb_{num}packets_1-0n0_1-37n1.npy"
        # rgb_str1 = f"rgb_{num}packets_1-0n0_1-37n1.npy"

        A_0 = np.load(results_path.joinpath(A_str0))
        # zgb_0 = np.load(results_path.joinpath(zgb_str0))
        # rgb_0 = np.load(results_path.joinpath(rgb_str0))
        A_1 = np.load(results_path.joinpath(A_str1))
        # zgb_1 = np.load(results_path.joinpath(zgb_str1))
        # rgb_1 = np.load(results_path.joinpath(rgb_str1))

        Az_0 = np.sum(A_0, axis=1)
        Az_norm0 = Az_0 / ( num * Dz )
        Fz_0 = Az_norm0 / ma
        Az_1 = np.sum(A_1, axis=1)
        Az_norm1 = Az_1 / ( num * Dz )
        Fz_1 = Az_norm1 / ma

        ax = axes[i]
        # ax.plot(x, Fz_0, label=f"$n$={n_rel0}")
        # ax.plot(x, Fz_1, label=f"$n$={n_rel1}")
        # ax.plot(x[:-1], Fz_0[:-1], label=f"$n$={n_rel0}")
        # ax.plot(x[:-1], Fz_1[:-1], label=f"$n$={n_rel1}")
        ax.plot(x[:-1], Fz_0[:-1], label="$n_{rel}$=1")
        ax.plot(x[:-1], Fz_1[:-1], label="$n_{rel}$=1.37")
        ax.set_yscale('log')
        ax.set_xlabel('z [cm]')
        ax.set_ylabel('Fluence [-]')
        ax.set_title(f"{num} packets")

        if i == 0:
            ax.legend()

    fig.suptitle("Comparisons of Internal Fluences as a Function of Depth")
    plt.tight_layout()
    plt.show()


"""
--------------------------------------------
Utility Classes
--------------------------------------------
"""

class Location:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"


class Direction:
    def __init__(self, mx, my, mz):
        self.mx = mx
        self.my = my
        self.mz = mz

    def __str__(self):
        return f"[{self.mx}, {self.my}, {self.mz}]"


class Photon:
    def __init__(self):
        self.weight = 1.0                       # current size of the photon packet
        self.loc = Location(0.0, 0.0, 0.0)      # current coordinate of the photon 
        self.dir = Direction(0.0, 0.0, 1.0)     # current direction of the photon
        self.s = 0.0                            # step size (dimensionless)
        self.dead = False                       # status of the photon size
        self.outofbounds = False                # status of the photon location
        self.Nz = 200                           # number of elements in the z dimension
        self.Nr = 66                            # number of elements in the r dimension
        self.res = 0.005                        # [cm], cell resolution for absorbance
        self.zmax = ( self.Nz - 1 ) * self.res  # [cm], max distance in z dim
        self.rmax = ( self.Nr - 1 ) * self.res  # [cm], max distance in r dim

    def __str__(self):
        return f"""
        Weight:\t\t{self.weight}
        Location:\t{self.loc}
        Direction:\t{self.dir}
        Step Size:\t{self.s}
        Dead?\t\t{self.dead}
        Out of Bounds?\t{self.outofbounds}
        """

    def move(self, d):
        # move the photon a certain distance d along its current direction
        self.loc.x = self.loc.x + self.dir.mx * d
        self.loc.y = self.loc.y + self.dir.my * d
        self.loc.z = self.loc.z + self.dir.mz * d

    def get_location(self):
        # return the location as a numpy array for equality checks
        return np.array([self.loc.x, self.loc.y, self.loc.z])
    
    def get_direction(self):
        # return the direction as a numpy array for equality checks
        return np.array([self.dir.mx, self.dir.my, self.dir.mz])

    def get_db(self):
        # return the distance to the boundary along the current path direction.
        if self.dir.mz >= 0:
            # if the photon isn't pointed at the boundary, it will never reach it
            db = np.inf
        else:
            db = ( 0 - self.loc.z ) / self.dir.mz
        return db

    def get_alpha_i(self):
        # return the angle of incidence alpha for the photon
        return np.arccos( np.abs( self.dir.mz ) )

    def get_delta_W(self, ma, mt):
        # return the fraction of weight absorbed by the medium
        return ( ma / mt ) * self.weight

    def get_reflectance(self, ni, nt):
        # return the reflectance of the photon given the refractive indices of tissue (ni) and air (nt)
        ai = np.arccos( np.abs( self.dir.mz ) )
        if DEBUG:
            print(f"\t\tni={ni}, nt={nt}, sin(ai)={np.sin(ai)}")
            print(f"quantity inside arcsin is {( ni / nt ) * np.sin( ai )}")
        at = np.arcsin( ( ni / nt ) * np.sin( ai ) )
        crit_angle = np.arcsin( nt / ni )
        if ni > nt and ai > crit_angle:
            # local reflectance equals unity
            Ri = 1
        else:
            c0 = ( np.sin( ai - at ) ** 2 ) / ( np.sin( ai + at ) ** 2 )
            c1 = ( np.tan( ai - at ) ** 2 ) / ( np.tan( ai + at ) ** 2 )
            Ri = 0.5 * ( c0 + c1 )
        return Ri

    def hit_boundary(self, db):
        # returns if the photon will reach the boundary or its desired endpoint first
        return db <= self.s

    def update_direction(self, theta, phi):
        # updates the direction cosines of the photon given the new polar (theta) and azimuthal (phi) angles of propagation
        mx = self.dir.mx
        my = self.dir.my
        mz = self.dir.mz

        cos_theta = np.cos( theta )
        sin_theta = np.sin( theta )
        cos_phi = np.cos( phi )
        sin_phi = np.sin( phi )


        if np.abs( mz ) > 0.99999:
            self.dir.mx = sin_theta * cos_phi
            self.dir.my = sin_theta * sin_phi
            self.dir.mz = np.sign( mz ) * cos_theta 
        else:
            num = sin_theta * ( mx * mz * cos_phi - my * sin_phi )
            den = np.sqrt( 1 - mz ** 2 )
            self.dir.mx = num / den + mx * cos_theta 

            num = sin_theta * ( my * mz * cos_phi + mx * sin_phi )
            den = np.sqrt( 1 - mz ** 2 )
            self.dir.my = num / den + my * cos_theta

            self.dir.mz = - np.sqrt( 1 - mz ** 2 ) * sin_theta * cos_phi + mz * cos_theta

    def deposit_weight(self, w, A, z_gb, r_gb):
        # distribute weight w into the absorbance array A based on the photon's current location.
        # if outside of the tracked area, but the photon weight into the appropriate 
        z = self.loc.z
        r = np.sqrt( self.loc.x ** 2 + self.loc.y ** 2 )
        p = (z, r)
        iz = int( z / self.res )
        ir = int( r / self.res )

        if DEBUG:
            print(f"\t\tz={z}, r={r}")

        if z > self.zmax:
            # we need to find the inverse weightings with regards to r, and place in z garbage bin
            if r > self.rmax:
                z_gb[-1] += w
            else:
                d_l = np.abs( r - ( ir * self.res ) )
                d_r = np.abs( r - ( ( ir + 1 ) * self.res ) )
                total_d_inv = ( 1 / d_l ) + ( 1 / d_r )
                c_l = ( 1 / d_l ) / total_d_inv
                c_r = ( 1 / d_r ) / total_d_inv
                z_gb[ir] += w * c_l
                z_gb[ir+1] += w * c_r

        if r > self.rmax:
            # we need to find the inverse weightings with regards to z, and place in r garbage bin
            if z > self.zmax:
                r_gb[-1] += w
            else:
                d_t = np.abs( z - ( iz * self.res ) )
                d_b = np.abs( z - ( ( iz + 1 ) * self.res ) )
                total_d_inv = ( 1 / d_t ) + ( 1 / d_b )
                c_t = ( 1 / d_t ) / total_d_inv
                c_b = ( 1 / d_b ) / total_d_inv
                r_gb[iz] += w * c_t
                r_gb[iz+1] += w * c_b

        if z <= self.zmax and r <= self.rmax:
            # we do the inverse weighting in both dimensions, and place in the absorbance array
            d_tl = get_distance( p, ( iz * self.res, ir * self.res ) )
            d_tr = get_distance( p, ( iz * self.res, ( ir + 1 ) * self.res ) )
            d_br = get_distance( p, ( ( iz + 1 ) * self.res, ( ir + 1 ) * self.res ) )
            d_bl = get_distance( p, ( ( iz + 1 ) * self.res, ir * self.res ) )

            total_d_inv = ( 1 / d_tl ) + ( 1 / d_tr ) + ( 1 / d_br ) + ( 1 / d_bl )
            c_tl = ( 1 / d_tl ) / total_d_inv
            c_tr = ( 1 / d_tr ) / total_d_inv
            c_br = ( 1 / d_br ) / total_d_inv
            c_bl = ( 1 / d_bl ) / total_d_inv

            A[iz, ir] += w * c_tl
            A[iz, ir+1] += w * c_tr
            A[iz+1, ir+1] += w * c_br
            A[iz+1, ir] += w * c_bl


class Simulation:
    def __init__(self, num_trials=1, n0=1.0, n1=1.0, output_dir=None):
        self.num_trials = num_trials
        self.n0 = n0
        self.n1 = n1
        self.output_dir = output_dir
        self.Rsp = specular_reflectance(n0, n1)
        self.ma = 0.1
        self.ms = 100
        self.mt = self.ma + self.ms
        self.g = 0.9
        self.Wth = 0.0001
        self.m = 10
        self.dzr = 0.005
        self.Nz = 200
        self.Nr = int( self.Nz / 3 )
        self.A = absorbance_matrix(self.Nz, self.Nr)
        self.z_gb = np.zeros(self.Nr)
        self.r_gb = np.zeros(self.Nz)

    def __str__(self):
        return f"""
        Number of Packets: {self.num_trials}  
        """

    def run_sim(self):
        # launch each of the photon packets
        for launch in tqdm(range(self.num_trials)):
        # for launch in range(self.num_trials):
            if DEBUG: 
                print(f"Photon {launch}")

            photon = Photon()

            # specular reflectance
            photon.weight -= self.Rsp

            count = 0
            # photon travel loop
            while True:
                count += 1

                if DEBUG:
                    print(f"\tInteraction {count}: w={photon.weight}")

                # set new s if s=0
                if photon.s == 0:
                    photon.s = sample_s(self.mt)

                # find distance to the boundary db
                db = photon.get_db()

                # hit boundary?
                if photon.hit_boundary(db):
                    # move db
                    photon.move(db)

                    # s = s - db
                    photon.s -= db

                    # transmit / reflect
                    Ri = photon.get_reflectance(self.n1, self.n0)
                    if gen_xi(1) <= Ri:
                        # photon packet is reflected
                        photon.dir.mz *= -1
                    else:
                        # transmitted
                        # (i don't think we track anything for this)
                        photon.dead = True
                else:
                    # move s
                    photon.move(photon.s)

                    # set s=0
                    photon.s = 0

                    # absorb
                    delta_W = photon.get_delta_W(self.ma, self.mt)
                    # reduce photon weight
                    photon.weight -= delta_W
                    # increase absorbance weight
                    if DEBUG:
                        print("\t\tcalling deposit:") 
                    photon.deposit_weight(delta_W, self.A, self.z_gb, self.r_gb)

                    # scatter
                    cos_theta = sample_cos_theta(self.g)
                    theta = np.arccos( cos_theta )
                    phi = sample_phi()
                    photon.update_direction(theta, phi) 

                # photon dead?
                if photon.dead:
                    break

                # weight small?
                if photon.weight >= self.Wth:
                    # no need to do roulette if weight is above the threshold
                    continue

                # survive roulette?
                if gen_xi(1) <= 1 / self.m:
                    W = self.m * photon.weight
                else:
                    W = 0
                if W == 0:
                    break

        print(f"Finished simulation of {self.num_trials} photons!")
        print("Saving arrays to file...")


        A_str = f"A_{self.num_trials}packets_{self.n0}n0_{self.n1}n1.npy".replace(".", "-")
        zgb_str = f"zgb_{self.num_trials}packets_{self.n0}n0_{self.n1}n1.npy".replace(".", "-")
        rgb_str = f"rgb_{self.num_trials}packets_{self.n0}n0_{self.n1}n1.npy".replace(".", "-")
        np.save(self.output_dir.joinpath(A_str), self.A)
        np.save(self.output_dir.joinpath(zgb_str), self.z_gb)
        np.save(self.output_dir.joinpath(rgb_str), self.r_gb)
        print("Done.")


