#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexfem.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmplex.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetscale_ DMPLEXGETSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetscale_ dmplexgetscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetscale_ DMPLEXSETSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetscale_ dmplexsetscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetuseceed_ DMPLEXGETUSECEED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetuseceed_ dmplexgetuseceed
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetuseceed_ DMPLEXSETUSECEED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetuseceed_ dmplexsetuseceed
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetusematclosurepermutation_ DMPLEXGETUSEMATCLOSUREPERMUTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetusematclosurepermutation_ dmplexgetusematclosurepermutation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetusematclosurepermutation_ DMPLEXSETUSEMATCLOSUREPERMUTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetusematclosurepermutation_ dmplexsetusematclosurepermutation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreaterigidbody_ DMPLEXCREATERIGIDBODY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreaterigidbody_ dmplexcreaterigidbody
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreaterigidbodies_ DMPLEXCREATERIGIDBODIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreaterigidbodies_ dmplexcreaterigidbodies
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetmaxprojectionheight_ DMPLEXSETMAXPROJECTIONHEIGHT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetmaxprojectionheight_ dmplexsetmaxprojectionheight
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetmaxprojectionheight_ DMPLEXGETMAXPROJECTIONHEIGHT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetmaxprojectionheight_ dmplexgetmaxprojectionheight
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexglobaltolocalbasis_ DMPLEXGLOBALTOLOCALBASIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexglobaltolocalbasis_ dmplexglobaltolocalbasis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlocaltoglobalbasis_ DMPLEXLOCALTOGLOBALBASIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlocaltoglobalbasis_ dmplexlocaltoglobalbasis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatebasisrotation_ DMPLEXCREATEBASISROTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatebasisrotation_ dmplexcreatebasisrotation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexinsertboundaryvalues_ DMPLEXINSERTBOUNDARYVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexinsertboundaryvalues_ dmplexinsertboundaryvalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexinserttimederivativeboundaryvalues_ DMPLEXINSERTTIMEDERIVATIVEBOUNDARYVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexinserttimederivativeboundaryvalues_ dmplexinserttimederivativeboundaryvalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputel2fluxdiffveclocal_ DMPLEXCOMPUTEL2FLUXDIFFVECLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputel2fluxdiffveclocal_ dmplexcomputel2fluxdiffveclocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputel2fluxdiffvec_ DMPLEXCOMPUTEL2FLUXDIFFVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputel2fluxdiffvec_ dmplexcomputel2fluxdiffvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeclementinterpolant_ DMPLEXCOMPUTECLEMENTINTERPOLANT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeclementinterpolant_ dmplexcomputeclementinterpolant
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputegradientclementinterpolant_ DMPLEXCOMPUTEGRADIENTCLEMENTINTERPOLANT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputegradientclementinterpolant_ dmplexcomputegradientclementinterpolant
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeintegralfem_ DMPLEXCOMPUTEINTEGRALFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeintegralfem_ dmplexcomputeintegralfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputecellwiseintegralfem_ DMPLEXCOMPUTECELLWISEINTEGRALFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputecellwiseintegralfem_ dmplexcomputecellwiseintegralfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeinterpolatornested_ DMPLEXCOMPUTEINTERPOLATORNESTED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeinterpolatornested_ dmplexcomputeinterpolatornested
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeinterpolatorgeneral_ DMPLEXCOMPUTEINTERPOLATORGENERAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeinterpolatorgeneral_ dmplexcomputeinterpolatorgeneral
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputemassmatrixgeneral_ DMPLEXCOMPUTEMASSMATRIXGENERAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputemassmatrixgeneral_ dmplexcomputemassmatrixgeneral
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeinjectorfem_ DMPLEXCOMPUTEINJECTORFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeinjectorfem_ dmplexcomputeinjectorfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetgeometryfvm_ DMPLEXGETGEOMETRYFVM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetgeometryfvm_ dmplexgetgeometryfvm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetgradientdm_ DMPLEXGETGRADIENTDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetgradientdm_ dmplexgetgradientdm
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexgetscale_(DM dm,PetscUnit *unit,PetscReal *scale, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(scale);
*ierr = DMPlexGetScale(
	(DM)PetscToPointer((dm) ),*unit,scale);
}
PETSC_EXTERN void  dmplexsetscale_(DM dm,PetscUnit *unit,PetscReal *scale, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetScale(
	(DM)PetscToPointer((dm) ),*unit,*scale);
}
PETSC_EXTERN void  dmplexgetuseceed_(DM dm,PetscBool *useCeed, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexGetUseCeed(
	(DM)PetscToPointer((dm) ),useCeed);
}
PETSC_EXTERN void  dmplexsetuseceed_(DM dm,PetscBool *useCeed, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetUseCeed(
	(DM)PetscToPointer((dm) ),*useCeed);
}
PETSC_EXTERN void  dmplexgetusematclosurepermutation_(DM dm,PetscBool *useClPerm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexGetUseMatClosurePermutation(
	(DM)PetscToPointer((dm) ),useClPerm);
}
PETSC_EXTERN void  dmplexsetusematclosurepermutation_(DM dm,PetscBool *useClPerm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetUseMatClosurePermutation(
	(DM)PetscToPointer((dm) ),*useClPerm);
}
PETSC_EXTERN void  dmplexcreaterigidbody_(DM dm,PetscInt *field,MatNullSpace *sp, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = DMPlexCreateRigidBody(
	(DM)PetscToPointer((dm) ),*field,sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
}
PETSC_EXTERN void  dmplexcreaterigidbodies_(DM dm,PetscInt *nb,DMLabel label, PetscInt nids[], PetscInt ids[],MatNullSpace *sp, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(nids);
CHKFORTRANNULLINTEGER(ids);
PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = DMPlexCreateRigidBodies(
	(DM)PetscToPointer((dm) ),*nb,
	(DMLabel)PetscToPointer((label) ),nids,ids,sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
}
PETSC_EXTERN void  dmplexsetmaxprojectionheight_(DM dm,PetscInt *height, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetMaxProjectionHeight(
	(DM)PetscToPointer((dm) ),*height);
}
PETSC_EXTERN void  dmplexgetmaxprojectionheight_(DM dm,PetscInt *height, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(height);
*ierr = DMPlexGetMaxProjectionHeight(
	(DM)PetscToPointer((dm) ),height);
}
PETSC_EXTERN void  dmplexglobaltolocalbasis_(DM dm,Vec lv, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(lv);
*ierr = DMPlexGlobalToLocalBasis(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((lv) ));
}
PETSC_EXTERN void  dmplexlocaltoglobalbasis_(DM dm,Vec lv, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(lv);
*ierr = DMPlexLocalToGlobalBasis(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((lv) ));
}
PETSC_EXTERN void  dmplexcreatebasisrotation_(DM dm,PetscReal *alpha,PetscReal *beta,PetscReal *gamma, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateBasisRotation(
	(DM)PetscToPointer((dm) ),*alpha,*beta,*gamma);
}
PETSC_EXTERN void  dmplexinsertboundaryvalues_(DM dm,PetscBool *insertEssential,Vec locX,PetscReal *time,Vec faceGeomFVM,Vec cellGeomFVM,Vec gradFVM, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX);
CHKFORTRANNULLOBJECT(faceGeomFVM);
CHKFORTRANNULLOBJECT(cellGeomFVM);
CHKFORTRANNULLOBJECT(gradFVM);
*ierr = DMPlexInsertBoundaryValues(
	(DM)PetscToPointer((dm) ),*insertEssential,
	(Vec)PetscToPointer((locX) ),*time,
	(Vec)PetscToPointer((faceGeomFVM) ),
	(Vec)PetscToPointer((cellGeomFVM) ),
	(Vec)PetscToPointer((gradFVM) ));
}
PETSC_EXTERN void  dmplexinserttimederivativeboundaryvalues_(DM dm,PetscBool *insertEssential,Vec locX_t,PetscReal *time,Vec faceGeomFVM,Vec cellGeomFVM,Vec gradFVM, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX_t);
CHKFORTRANNULLOBJECT(faceGeomFVM);
CHKFORTRANNULLOBJECT(cellGeomFVM);
CHKFORTRANNULLOBJECT(gradFVM);
*ierr = DMPlexInsertTimeDerivativeBoundaryValues(
	(DM)PetscToPointer((dm) ),*insertEssential,
	(Vec)PetscToPointer((locX_t) ),*time,
	(Vec)PetscToPointer((faceGeomFVM) ),
	(Vec)PetscToPointer((cellGeomFVM) ),
	(Vec)PetscToPointer((gradFVM) ));
}
PETSC_EXTERN void  dmplexcomputel2fluxdiffveclocal_(Vec lu,PetscInt *f,Vec lmu,PetscInt *mf,Vec eFlux, int *ierr)
{
CHKFORTRANNULLOBJECT(lu);
CHKFORTRANNULLOBJECT(lmu);
CHKFORTRANNULLOBJECT(eFlux);
*ierr = DMPlexComputeL2FluxDiffVecLocal(
	(Vec)PetscToPointer((lu) ),*f,
	(Vec)PetscToPointer((lmu) ),*mf,
	(Vec)PetscToPointer((eFlux) ));
}
PETSC_EXTERN void  dmplexcomputel2fluxdiffvec_(Vec u,PetscInt *f,Vec mu,PetscInt *mf,Vec eFlux, int *ierr)
{
CHKFORTRANNULLOBJECT(u);
CHKFORTRANNULLOBJECT(mu);
CHKFORTRANNULLOBJECT(eFlux);
*ierr = DMPlexComputeL2FluxDiffVec(
	(Vec)PetscToPointer((u) ),*f,
	(Vec)PetscToPointer((mu) ),*mf,
	(Vec)PetscToPointer((eFlux) ));
}
PETSC_EXTERN void  dmplexcomputeclementinterpolant_(DM dm,Vec locX,Vec locC, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX);
CHKFORTRANNULLOBJECT(locC);
*ierr = DMPlexComputeClementInterpolant(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((locX) ),
	(Vec)PetscToPointer((locC) ));
}
PETSC_EXTERN void  dmplexcomputegradientclementinterpolant_(DM dm,Vec locX,Vec locC, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX);
CHKFORTRANNULLOBJECT(locC);
*ierr = DMPlexComputeGradientClementInterpolant(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((locX) ),
	(Vec)PetscToPointer((locC) ));
}
PETSC_EXTERN void  dmplexcomputeintegralfem_(DM dm,Vec X,PetscScalar *integral,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLSCALAR(integral);
*ierr = DMPlexComputeIntegralFEM(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),integral,user);
}
PETSC_EXTERN void  dmplexcomputecellwiseintegralfem_(DM dm,Vec X,Vec F,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(F);
*ierr = DMPlexComputeCellwiseIntegralFEM(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((F) ),user);
}
PETSC_EXTERN void  dmplexcomputeinterpolatornested_(DM dmc,DM dmf,PetscBool *isRefined,Mat In,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dmc);
CHKFORTRANNULLOBJECT(dmf);
CHKFORTRANNULLOBJECT(In);
*ierr = DMPlexComputeInterpolatorNested(
	(DM)PetscToPointer((dmc) ),
	(DM)PetscToPointer((dmf) ),*isRefined,
	(Mat)PetscToPointer((In) ),user);
}
PETSC_EXTERN void  dmplexcomputeinterpolatorgeneral_(DM dmc,DM dmf,Mat In,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dmc);
CHKFORTRANNULLOBJECT(dmf);
CHKFORTRANNULLOBJECT(In);
*ierr = DMPlexComputeInterpolatorGeneral(
	(DM)PetscToPointer((dmc) ),
	(DM)PetscToPointer((dmf) ),
	(Mat)PetscToPointer((In) ),user);
}
PETSC_EXTERN void  dmplexcomputemassmatrixgeneral_(DM dmc,DM dmf,Mat mass,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dmc);
CHKFORTRANNULLOBJECT(dmf);
CHKFORTRANNULLOBJECT(mass);
*ierr = DMPlexComputeMassMatrixGeneral(
	(DM)PetscToPointer((dmc) ),
	(DM)PetscToPointer((dmf) ),
	(Mat)PetscToPointer((mass) ),user);
}
PETSC_EXTERN void  dmplexcomputeinjectorfem_(DM dmc,DM dmf,VecScatter *sc,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dmc);
CHKFORTRANNULLOBJECT(dmf);
*ierr = DMPlexComputeInjectorFEM(
	(DM)PetscToPointer((dmc) ),
	(DM)PetscToPointer((dmf) ),sc,user);
}
PETSC_EXTERN void  dmplexgetgeometryfvm_(DM dm,Vec *facegeom,Vec *cellgeom,PetscReal *minRadius, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool facegeom_null = !*(void**) facegeom ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(facegeom);
PetscBool cellgeom_null = !*(void**) cellgeom ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cellgeom);
CHKFORTRANNULLREAL(minRadius);
*ierr = DMPlexGetGeometryFVM(
	(DM)PetscToPointer((dm) ),facegeom,cellgeom,minRadius);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! facegeom_null && !*(void**) facegeom) * (void **) facegeom = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cellgeom_null && !*(void**) cellgeom) * (void **) cellgeom = (void *)-2;
}
PETSC_EXTERN void  dmplexgetgradientdm_(DM dm,PetscFV fv,DM *dmGrad, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(fv);
PetscBool dmGrad_null = !*(void**) dmGrad ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmGrad);
*ierr = DMPlexGetGradientDM(
	(DM)PetscToPointer((dm) ),
	(PetscFV)PetscToPointer((fv) ),dmGrad);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmGrad_null && !*(void**) dmGrad) * (void **) dmGrad = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
